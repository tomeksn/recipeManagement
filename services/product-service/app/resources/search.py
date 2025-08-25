"""Advanced search resource endpoints."""
import structlog
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields, validate

from ..services.search_service import ProductSearchService
from ..schemas.product import ErrorResponseSchema

logger = structlog.get_logger("product_service.search")
blp = Blueprint('search', __name__, url_prefix='/api/v1/search', description='Advanced search operations')


class AdvancedSearchSchema(Schema):
    """Schema for advanced search request."""
    
    q = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={'description': 'Search query'}
    )
    type = fields.Str(
        validate=validate.OneOf(['standard', 'kit', 'semi-product']),
        metadata={'description': 'Filter by product type'}
    )
    unit = fields.Str(
        validate=validate.OneOf(['piece', 'gram']),
        metadata={'description': 'Filter by product unit'}
    )
    category_id = fields.UUID(
        metadata={'description': 'Filter by category UUID'}
    )
    tag_id = fields.UUID(
        metadata={'description': 'Filter by tag UUID'}
    )
    limit = fields.Int(
        validate=validate.Range(min=1, max=100),
        missing=20,
        metadata={'description': 'Maximum number of results'}
    )
    similarity_threshold = fields.Float(
        validate=validate.Range(min=0.0, max=1.0),
        missing=0.3,
        metadata={'description': 'Minimum similarity threshold (0.0-1.0)'}
    )
    include_suggestions = fields.Bool(
        missing=True,
        metadata={'description': 'Include search suggestions in response'}
    )


class SearchSuggestionsSchema(Schema):
    """Schema for search suggestions request."""
    
    q = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        metadata={'description': 'Partial search query'}
    )
    limit = fields.Int(
        validate=validate.Range(min=1, max=20),
        missing=10,
        metadata={'description': 'Maximum number of suggestions'}
    )


class AdvancedSearchResponseSchema(Schema):
    """Schema for advanced search response."""
    
    results = fields.List(fields.Dict(), required=True)
    suggestions = fields.List(fields.Str(), required=True)
    query = fields.Str(required=True)
    normalized_query = fields.Str(required=True)
    total_results = fields.Int(required=True)
    search_time_ms = fields.Int(required=True)
    filters_applied = fields.Dict(required=True)


class SearchSuggestionsResponseSchema(Schema):
    """Schema for search suggestions response."""
    
    suggestions = fields.List(fields.Str(), required=True)
    query = fields.Str(required=True)
    total_suggestions = fields.Int(required=True)


class PopularSearchesResponseSchema(Schema):
    """Schema for popular searches response."""
    
    popular_searches = fields.List(fields.Dict(), required=True)
    total_count = fields.Int(required=True)


@blp.route('/')
class AdvancedSearch(MethodView):
    """Advanced search endpoint with filters and suggestions."""
    
    def __init__(self):
        self.search_service = ProductSearchService()
    
    @blp.arguments(AdvancedSearchSchema, location='query')
    @blp.response(200, AdvancedSearchResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid search parameters')
    def get(self, search_args):
        """Perform advanced product search.
        
        Search products with advanced filtering, fuzzy matching, and intelligent suggestions.
        Supports filtering by type, unit, category, and tag while providing search suggestions
        when few results are found.
        """
        logger.info("Performing advanced search", query=search_args['q'])
        
        try:
            # Extract filters from search args
            filters = {}
            for filter_key in ['type', 'unit', 'category_id', 'tag_id']:
                if filter_key in search_args and search_args[filter_key] is not None:
                    filters[filter_key] = search_args[filter_key]
            
            # Perform search
            result = self.search_service.advanced_search(
                query=search_args['q'],
                filters=filters,
                limit=search_args['limit'],
                similarity_threshold=search_args['similarity_threshold'],
                include_suggestions=search_args['include_suggestions']
            )
            
            logger.info("Advanced search completed", 
                       query=search_args['q'],
                       results_count=result['total_results'],
                       search_time_ms=result['search_time_ms'])
            
            return result
            
        except Exception as e:
            logger.error("Error performing advanced search", 
                        query=search_args['q'], 
                        error=str(e))
            abort(500, message="Internal server error while performing search")


@blp.route('/suggestions')
class SearchSuggestions(MethodView):
    """Search suggestions endpoint for autocomplete."""
    
    def __init__(self):
        self.search_service = ProductSearchService()
    
    @blp.arguments(SearchSuggestionsSchema, location='query')
    @blp.response(200, SearchSuggestionsResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid query parameters')
    def get(self, query_args):
        """Get search suggestions for autocomplete.
        
        Provide intelligent search suggestions based on partial query input.
        Useful for implementing autocomplete functionality in the frontend.
        """
        logger.info("Getting search suggestions", partial_query=query_args['q'])
        
        try:
            suggestions = self.search_service.get_search_suggestions(
                partial_query=query_args['q'],
                limit=query_args['limit']
            )
            
            result = {
                'suggestions': suggestions,
                'query': query_args['q'],
                'total_suggestions': len(suggestions)
            }
            
            logger.info("Search suggestions retrieved", 
                       partial_query=query_args['q'],
                       suggestions_count=len(suggestions))
            
            return result
            
        except Exception as e:
            logger.error("Error getting search suggestions",
                        partial_query=query_args['q'],
                        error=str(e))
            abort(500, message="Internal server error while getting suggestions")


@blp.route('/popular')
class PopularSearches(MethodView):
    """Popular searches endpoint."""
    
    def __init__(self):
        self.search_service = ProductSearchService()
    
    @blp.response(200, PopularSearchesResponseSchema)
    def get(self):
        """Get popular search terms.
        
        Retrieve the most frequently searched terms to help users discover
        popular products and improve search experience.
        """
        logger.info("Getting popular searches")
        
        try:
            popular_searches = self.search_service.get_popular_searches(limit=10)
            
            result = {
                'popular_searches': popular_searches,
                'total_count': len(popular_searches)
            }
            
            logger.info("Popular searches retrieved", count=len(popular_searches))
            return result
            
        except Exception as e:
            logger.error("Error getting popular searches", error=str(e))
            abort(500, message="Internal server error while getting popular searches")


@blp.route('/cache/cleanup')
class SearchCacheCleanup(MethodView):
    """Search cache cleanup endpoint (for maintenance)."""
    
    def __init__(self):
        self.search_service = ProductSearchService()
    
    @blp.response(200, schema={'type': 'object', 'properties': {'cleaned_entries': {'type': 'integer'}}})
    def delete(self):
        """Clean up expired search cache entries.
        
        Remove expired entries from the search cache to optimize performance.
        This endpoint is typically called by maintenance tasks.
        """
        logger.info("Cleaning up expired search cache")
        
        try:
            cleaned_count = self.search_service.cleanup_expired_cache()
            
            result = {'cleaned_entries': cleaned_count}
            
            logger.info("Search cache cleanup completed", cleaned_entries=cleaned_count)
            return result
            
        except Exception as e:
            logger.error("Error cleaning up search cache", error=str(e))
            abort(500, message="Internal server error while cleaning cache")