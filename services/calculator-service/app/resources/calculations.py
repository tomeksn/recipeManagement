"""Calculation API resources for Calculator Service."""
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields, validate, ValidationError, post_load

from ..services.calculation_service import calculation_service
from ..utils.exceptions import CalculationError

blp = Blueprint(
    'calculations',
    __name__,
    url_prefix='/api/v1/calculations',
    description='Recipe calculation endpoints'
)


class IngredientCalculationSchema(Schema):
    """Schema for individual ingredient calculation."""
    product_id = fields.UUID(required=True, description="Product UUID")
    product_name = fields.Str(dump_only=True, description="Product name")
    original_quantity = fields.Float(required=True, description="Original quantity")
    calculated_quantity = fields.Float(dump_only=True, description="Calculated quantity")
    unit = fields.Str(required=True, validate=validate.OneOf(['piece', 'gram']), 
                      description="Unit type")
    order = fields.Int(description="Display order")


class CalculationRequestSchema(Schema):
    """Schema for calculation request."""
    product_id = fields.UUID(required=True, description="Product UUID to calculate")
    target_quantity = fields.Float(required=True, validate=validate.Range(min=0.001),
                                   description="Target quantity")
    target_unit = fields.Str(required=True, validate=validate.OneOf(['piece', 'gram']),
                            description="Target unit type")
    include_hierarchy = fields.Bool(missing=False, description="Include sub-recipe expansion")
    max_depth = fields.Int(missing=5, validate=validate.Range(min=1, max=10),
                          description="Maximum hierarchy depth")
    precision = fields.Int(missing=None, validate=validate.Range(min=0, max=6),
                          description="Decimal precision (null for default)")


class CalculationResultSchema(Schema):
    """Schema for calculation result."""
    product_id = fields.UUID(required=True, description="Product UUID")
    product_name = fields.Str(description="Product name")
    target_quantity = fields.Float(required=True, description="Target quantity")
    target_unit = fields.Str(required=True, description="Target unit")
    scale_factor = fields.Float(required=True, description="Applied scale factor")
    original_yield = fields.Float(description="Original recipe yield")
    original_yield_unit = fields.Str(description="Original yield unit")
    ingredients = fields.List(fields.Nested(IngredientCalculationSchema), 
                             description="Calculated ingredients")
    calculation_metadata = fields.Dict(description="Calculation metadata")
    cached = fields.Bool(description="Result served from cache")
    calculation_time_ms = fields.Float(description="Calculation time in milliseconds")


class BatchCalculationRequestSchema(Schema):
    """Schema for batch calculation request."""
    calculations = fields.List(
        fields.Nested(CalculationRequestSchema),
        required=True,
        validate=validate.Length(min=1, max=50),
        description="List of calculations to perform"
    )


class BatchCalculationResultSchema(Schema):
    """Schema for batch calculation result."""
    results = fields.List(fields.Nested(CalculationResultSchema),
                         description="Calculation results")
    summary = fields.Dict(description="Batch calculation summary")


class CalculationHistorySchema(Schema):
    """Schema for calculation history entry."""
    id = fields.UUID(dump_only=True, description="History entry ID")
    product_id = fields.UUID(required=True, description="Product UUID")
    target_quantity = fields.Float(required=True, description="Target quantity")
    target_unit = fields.Str(required=True, description="Target unit")
    scale_factor = fields.Float(description="Applied scale factor")
    created_at = fields.DateTime(dump_only=True, description="Calculation timestamp")
    calculation_time_ms = fields.Float(description="Calculation time")


@blp.route('/calculate')
class Calculate(MethodView):
    """Single recipe calculation endpoint."""
    
    @blp.arguments(CalculationRequestSchema)
    @blp.response(200, CalculationResultSchema)
    @blp.alt_response(404, description="Recipe not found")
    @blp.alt_response(400, description="Invalid calculation parameters")
    def post(self, calculation_request):
        """Calculate ingredient quantities for a recipe.
        
        Performs scaling calculations for a recipe based on target quantity.
        Supports both piece-based and weight-based scaling with optional
        hierarchical expansion for semi-products.
        
        **Calculation Types:**
        
        - **Piece-based**: Multiply all ingredients by scale factor
        - **Weight-based**: Scale ingredients proportionally by weight
        - **Mixed units**: Handle both piece and gram ingredients appropriately
        
        **Hierarchical Expansion:**
        
        When `include_hierarchy=true`, semi-products in ingredients are
        expanded to show their own recipe components, creating a multi-level
        ingredient breakdown.
        """
        try:
            result = calculation_service.calculate_recipe(
                product_id=str(calculation_request['product_id']),
                target_quantity=calculation_request['target_quantity'],
                target_unit=calculation_request['target_unit'],
                include_hierarchy=calculation_request['include_hierarchy'],
                max_depth=calculation_request['max_depth'],
                precision=calculation_request['precision']
            )
            return result
            
        except CalculationError as e:
            current_app.logger.error(f"Calculation error: {str(e)}")
            blp.abort(400, message=str(e))
        except ValueError as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            blp.abort(400, message=f"Invalid parameters: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Unexpected calculation error: {str(e)}")
            blp.abort(500, message="Internal calculation error")


@blp.route('/calculate/batch')
class BatchCalculate(MethodView):
    """Batch recipe calculation endpoint."""
    
    @blp.arguments(BatchCalculationRequestSchema)
    @blp.response(200, BatchCalculationResultSchema)
    @blp.alt_response(400, description="Invalid batch request")
    def post(self, batch_request):
        """Calculate multiple recipes in a single request.
        
        Performs batch calculations with optimized performance through
        parallel processing and shared caching. Useful for calculating
        multiple recipes simultaneously or comparing different quantities.
        
        **Performance Benefits:**
        
        - Parallel calculation processing
        - Shared recipe data fetching
        - Bulk cache operations
        - Reduced network overhead
        """
        try:
            results = calculation_service.calculate_batch(
                batch_request['calculations']
            )
            return results
            
        except CalculationError as e:
            current_app.logger.error(f"Batch calculation error: {str(e)}")
            blp.abort(400, message=str(e))
        except Exception as e:
            current_app.logger.error(f"Unexpected batch calculation error: {str(e)}")
            blp.abort(500, message="Internal batch calculation error")


class HistoryQuerySchema(Schema):
    """Schema for history query parameters."""
    product_id = fields.UUID(missing=None, description="Filter by product")
    limit = fields.Int(missing=50, validate=validate.Range(min=1, max=500),
                       description="Maximum results")
    offset = fields.Int(missing=0, validate=validate.Range(min=0),
                            description="Results offset")


@blp.route('/history')
class CalculationHistory(MethodView):
    """Calculation history endpoint."""
    
    @blp.arguments(HistoryQuerySchema, location='query')
    @blp.response(200, CalculationHistorySchema(many=True))
    def get(self, query_args):
        """Get calculation history.
        
        Returns a paginated list of previous calculations for auditing
        and analytics purposes. Can be filtered by product ID.
        """
        try:
            history = calculation_service.get_calculation_history(
                product_id=query_args.get('product_id'),
                limit=query_args['limit'],
                offset=query_args['offset']
            )
            return history
            
        except Exception as e:
            current_app.logger.error(f"History retrieval error: {str(e)}")
            blp.abort(500, message="Failed to retrieve calculation history")


@blp.route('/cache/stats')
class CacheStats(MethodView):
    """Cache statistics endpoint."""
    
    @blp.response(200, {
        'total_keys': fields.Int(description="Total cached calculations"),
        'hit_rate': fields.Float(description="Cache hit rate percentage"),
        'memory_usage': fields.Dict(description="Memory usage statistics"),
        'top_products': fields.List(fields.Dict(), description="Most calculated products")
    })
    def get(self):
        """Get calculation cache statistics.
        
        Returns performance metrics about the calculation cache
        including hit rates, memory usage, and popular calculations.
        """
        try:
            stats = calculation_service.get_cache_stats()
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Cache stats error: {str(e)}")
            blp.abort(500, message="Failed to retrieve cache statistics")


@blp.route('/cache/clear')
class CacheClear(MethodView):
    """Cache management endpoint."""
    
    @blp.arguments({
        'product_id': fields.UUID(missing=None, description="Clear specific product cache"),
        'confirm': fields.Bool(required=True, description="Confirmation flag")
    })
    @blp.response(200, {
        'cleared_keys': fields.Int(description="Number of cache keys cleared"),
        'message': fields.Str(description="Confirmation message")
    })
    def post(self, clear_request):
        """Clear calculation cache.
        
        Clears cached calculation results. Can clear all cache or
        just cache for a specific product. Requires confirmation.
        """
        if not clear_request['confirm']:
            blp.abort(400, message="Cache clear operation requires confirmation")
        
        try:
            result = calculation_service.clear_cache(
                product_id=clear_request.get('product_id')
            )
            return result
            
        except Exception as e:
            current_app.logger.error(f"Cache clear error: {str(e)}")
            blp.abort(500, message="Failed to clear cache")