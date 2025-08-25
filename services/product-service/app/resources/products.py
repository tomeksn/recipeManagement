"""Product resource endpoints."""
import structlog
from uuid import UUID
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError

from ..services.product_repository import ProductRepository, CategoryRepository, TagRepository
from ..schemas.product import (
    ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema,
    ProductListSchema, ProductListQuerySchema, ProductSearchSchema,
    ProductSearchResponseSchema, ErrorResponseSchema
)
from ..utils.exceptions import ProductNotFoundError, ProductAlreadyExistsError
from ..models.product import ProductType, ProductUnit

logger = structlog.get_logger("product_service.resources")
blp = Blueprint('products', __name__, url_prefix='/api/v1/products', description='Product operations')


@blp.route('/')
class ProductCollection(MethodView):
    """Product collection endpoints."""
    
    def __init__(self):
        self.repository = ProductRepository()
    
    def get(self):
        """Get list of products with pagination and filtering.
        
        Retrieve a paginated list of products with optional filtering by type, unit,
        category, or tag. Supports pagination with configurable page size.
        """
        logger.info("Fetching product list")
        
        try:
            # Get products from repository with defaults
            products, pagination_meta = self.repository.get_all(
                page=1,
                per_page=20,
                include_relationships=False
            )
            
            # Convert to dict format
            products_data = []
            for product in products:
                product_dict = product.to_dict(include_relationships=False)
                products_data.append(product_dict)
            
            result = {
                'products': products_data,
                'pagination': pagination_meta
            }
            
            logger.info("Product list fetched successfully", count=len(products_data))
            return result
            
        except Exception as e:
            logger.error("Error fetching product list", error=str(e))
            abort(500, message="Internal server error while fetching products")
    
    @blp.arguments(ProductCreateSchema)
    @blp.response(201, ProductResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid product data')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Product already exists')
    def post(self, product_data):
        """Create a new product.
        
        Create a new product with the provided data. Product names must be unique.
        Categories and tags can be assigned during creation.
        """
        logger.info("Creating new product", name=product_data['name'])
        
        try:
            # TODO: Get user ID from authentication context
            created_by = None  # Will be implemented with authentication
            
            product = self.repository.create(product_data, created_by)
            
            # Return product with relationships
            result = product.to_dict(include_relationships=True)
            
            logger.info("Product created successfully", product_id=str(product.id))
            return result, 201
            
        except ProductAlreadyExistsError as e:
            logger.warning("Product creation failed - name already exists", name=product_data['name'])
            abort(409, message=str(e))
        except ValidationError as e:
            logger.warning("Product creation failed - validation error", errors=e.messages)
            abort(400, message="Validation failed", details=e.messages)
        except Exception as e:
            logger.error("Error creating product", error=str(e))
            abort(500, message="Internal server error while creating product")


@blp.route('/<uuid:product_id>')
class ProductItem(MethodView):
    """Individual product endpoints."""
    
    def __init__(self):
        self.repository = ProductRepository()
    
    @blp.response(200, ProductResponseSchema)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Product not found')
    def get(self, product_id):
        """Get a single product by ID.
        
        Retrieve detailed information about a specific product including
        its categories and tags.
        """
        logger.info("Fetching product", product_id=str(product_id))
        
        try:
            product = self.repository.get_by_id(product_id, include_relationships=True)
            
            if not product:
                logger.warning("Product not found", product_id=str(product_id))
                abort(404, message=f"Product with ID {product_id} not found")
            
            result = product.to_dict(include_relationships=True)
            
            logger.info("Product fetched successfully", product_id=str(product_id))
            return result
            
        except Exception as e:
            logger.error("Error fetching product", product_id=str(product_id), error=str(e))
            abort(500, message="Internal server error while fetching product")
    
    @blp.arguments(ProductUpdateSchema)
    @blp.response(200, ProductResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid product data')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Product not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Product name already exists')
    def put(self, product_data, product_id):
        """Update a product.
        
        Update an existing product with the provided data. Only provided fields
        will be updated. Product names must remain unique.
        """
        logger.info("Updating product", product_id=str(product_id), data=product_data)
        
        try:
            # TODO: Get user ID from authentication context
            updated_by = None  # Will be implemented with authentication
            
            product = self.repository.update(product_id, product_data, updated_by)
            
            # Return updated product with relationships
            result = product.to_dict(include_relationships=True)
            
            logger.info("Product updated successfully", product_id=str(product_id))
            return result
            
        except ProductNotFoundError as e:
            logger.warning("Product update failed - not found", product_id=str(product_id))
            abort(404, message=str(e))
        except ProductAlreadyExistsError as e:
            logger.warning("Product update failed - name already exists", 
                         product_id=str(product_id), name=product_data.get('name'))
            abort(409, message=str(e))
        except ValidationError as e:
            logger.warning("Product update failed - validation error", 
                         product_id=str(product_id), errors=e.messages)
            abort(400, message="Validation failed", details=e.messages)
        except Exception as e:
            logger.error("Error updating product", product_id=str(product_id), error=str(e))
            abort(500, message="Internal server error while updating product")
    
    @blp.response(204)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Product not found')
    def delete(self, product_id):
        """Delete a product.
        
        Permanently delete a product. This action cannot be undone.
        All associations with categories and tags will also be removed.
        """
        logger.info("Deleting product", product_id=str(product_id))
        
        try:
            success = self.repository.delete(product_id)
            
            if not success:
                logger.warning("Product deletion failed - not found", product_id=str(product_id))
                abort(404, message=f"Product with ID {product_id} not found")
            
            logger.info("Product deleted successfully", product_id=str(product_id))
            return '', 204
            
        except Exception as e:
            logger.error("Error deleting product", product_id=str(product_id), error=str(e))
            abort(500, message="Internal server error while deleting product")


@blp.route('/search')
class ProductSearch(MethodView):
    """Product search endpoints."""
    
    def __init__(self):
        self.repository = ProductRepository()
    
    @blp.arguments(ProductSearchSchema, location='query')
    @blp.response(200, ProductSearchResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid search parameters')
    def get(self, search_args):
        """Search products with fuzzy matching.
        
        Perform fuzzy search on product names with configurable similarity threshold.
        Results are ranked by similarity score.
        """
        logger.info("Searching products", query=search_args['q'])
        
        try:
            results = self.repository.search_fuzzy(
                search_term=search_args['q'],
                limit=search_args['limit'],
                similarity_threshold=search_args['similarity_threshold']
            )
            
            response = {
                'results': results,
                'query': search_args['q'],
                'total_results': len(results)
            }
            
            logger.info("Product search completed", 
                       query=search_args['q'], 
                       results_count=len(results))
            return response
            
        except Exception as e:
            logger.error("Error searching products", query=search_args['q'], error=str(e))
            abort(500, message="Internal server error while searching products")


@blp.route('/categories')
class CategoryCollection(MethodView):
    """Category collection endpoints."""
    
    def __init__(self):
        self.repository = CategoryRepository()
    
    @blp.response(200, schema={'type': 'array', 'items': {'$ref': '#/components/schemas/ProductCategory'}})
    def get(self):
        """Get all product categories.
        
        Retrieve a list of all available product categories.
        """
        logger.info("Fetching all categories")
        
        try:
            categories = self.repository.get_all()
            result = [category.to_dict() for category in categories]
            
            logger.info("Categories fetched successfully", count=len(result))
            return result
            
        except Exception as e:
            logger.error("Error fetching categories", error=str(e))
            abort(500, message="Internal server error while fetching categories")


@blp.route('/tags')
class TagCollection(MethodView):
    """Tag collection endpoints."""
    
    def __init__(self):
        self.repository = TagRepository()
    
    @blp.response(200, schema={'type': 'array', 'items': {'$ref': '#/components/schemas/ProductTag'}})
    def get(self):
        """Get all product tags.
        
        Retrieve a list of all available product tags.
        """
        logger.info("Fetching all tags")
        
        try:
            tags = self.repository.get_all()
            result = [tag.to_dict() for tag in tags]
            
            logger.info("Tags fetched successfully", count=len(result))
            return result
            
        except Exception as e:
            logger.error("Error fetching tags", error=str(e))
            abort(500, message="Internal server error while fetching tags")