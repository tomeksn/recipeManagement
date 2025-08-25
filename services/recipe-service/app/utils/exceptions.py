"""Custom exceptions and error handlers for the Recipe Service."""
import structlog
from flask import Flask, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

from ..services.product_client import ProductServiceError

logger = structlog.get_logger("recipe_service.exceptions")


class RecipeServiceError(Exception):
    """Base exception for Recipe Service."""
    
    def __init__(self, message: str, status_code: int = 500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload


class RecipeNotFoundError(RecipeServiceError):
    """Recipe not found exception."""
    
    def __init__(self, recipe_id: str):
        super().__init__(f"Recipe with ID {recipe_id} not found", 404)


class RecipeIngredientNotFoundError(RecipeServiceError):
    """Recipe ingredient not found exception."""
    
    def __init__(self, ingredient_id: str):
        super().__init__(f"Recipe ingredient with ID {ingredient_id} not found", 404)


class CircularDependencyError(RecipeServiceError):
    """Circular dependency in recipe hierarchy exception."""
    
    def __init__(self, product_id: str, existing_path: list = None):
        path_str = " -> ".join(existing_path) if existing_path else ""
        message = f"Circular dependency detected for product {product_id}"
        if path_str:
            message += f" in path: {path_str}"
        super().__init__(message, 400)


class InvalidProductError(RecipeServiceError):
    """Invalid product reference exception."""
    
    def __init__(self, product_id: str):
        super().__init__(f"Product with ID {product_id} does not exist", 400)


class RecipeValidationError(RecipeServiceError):
    """Recipe validation error exception."""
    
    def __init__(self, message: str, errors: dict = None):
        super().__init__(message, 400)
        self.errors = errors or {}


class MaxDepthExceededError(RecipeServiceError):
    """Maximum recipe depth exceeded exception."""
    
    def __init__(self, max_depth: int):
        super().__init__(f"Recipe hierarchy depth exceeds maximum allowed depth of {max_depth}", 400)


class TooManyIngredientsError(RecipeServiceError):
    """Too many ingredients in recipe exception."""
    
    def __init__(self, max_ingredients: int):
        super().__init__(f"Recipe exceeds maximum allowed ingredients ({max_ingredients})", 400)


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(RecipeServiceError)
    def handle_recipe_service_error(error: RecipeServiceError):
        """Handle custom Recipe Service errors."""
        logger.error(
            "Recipe service error",
            error=error.message,
            status_code=error.status_code,
            payload=error.payload
        )
        
        response = {
            'error': error.message,
            'status_code': error.status_code
        }
        
        if error.payload:
            response['details'] = error.payload
            
        return jsonify(response), error.status_code
    
    @app.errorhandler(ProductServiceError)
    def handle_product_service_error(error: ProductServiceError):
        """Handle Product Service communication errors."""
        logger.error(
            "Product service communication error",
            error=str(error),
            status_code=getattr(error, 'status_code', None)
        )
        
        status_code = getattr(error, 'status_code', 503)
        return jsonify({
            'error': 'External service communication failed',
            'status_code': status_code,
            'details': {'message': str(error)}
        }), status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        """Handle Marshmallow validation errors."""
        logger.warning(
            "Validation error",
            errors=error.messages if hasattr(error, 'messages') else str(error)
        )
        
        if hasattr(error, 'messages'):
            return jsonify({
                'error': 'Validation failed',
                'status_code': 400,
                'details': error.messages
            }), 400
        else:
            return jsonify({
                'error': 'Validation failed',
                'status_code': 400,
                'details': {'message': str(error)}
            }), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error: IntegrityError):
        """Handle database integrity errors."""
        logger.error("Database integrity error", error=str(error))
        
        # Parse common integrity errors
        error_msg = str(error.orig)
        
        if 'unique constraint' in error_msg.lower():
            if 'recipes_product_id_unique' in error_msg:
                return jsonify({
                    'error': 'Recipe for this product already exists',
                    'status_code': 409,
                    'details': {'field': 'product_id', 'message': 'A recipe for this product already exists'}
                }), 409
        
        if 'foreign key' in error_msg.lower():
            return jsonify({
                'error': 'Invalid reference to related entity',
                'status_code': 400,
                'details': {'message': 'Referenced entity does not exist'}
            }), 400
        
        return jsonify({
            'error': 'Database constraint violation',
            'status_code': 409,
            'details': {'message': 'The operation violates a database constraint'}
        }), 409
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error: SQLAlchemyError):
        """Handle general database errors."""
        logger.error("Database error", error=str(error))
        
        return jsonify({
            'error': 'Database error occurred',
            'status_code': 500,
            'details': {'message': 'An internal database error occurred'}
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(
            "HTTP exception",
            status_code=error.code,
            description=error.description
        )
        
        return jsonify({
            'error': error.name,
            'status_code': error.code,
            'details': {'message': error.description}
        }), error.code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Resource not found',
            'status_code': 404,
            'details': {'message': 'The requested resource was not found'}
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            'error': 'Method not allowed',
            'status_code': 405,
            'details': {'message': 'The HTTP method is not allowed for this resource'}
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors."""
        logger.error("Internal server error", error=str(error))
        
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500,
            'details': {'message': 'An unexpected error occurred'}
        }), 500