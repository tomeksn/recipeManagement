"""Custom exceptions and error handlers for the Product Service."""
import structlog
from flask import Flask, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException

logger = structlog.get_logger("product_service.exceptions")


class ProductServiceError(Exception):
    """Base exception for Product Service."""
    
    def __init__(self, message: str, status_code: int = 500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload


class ProductNotFoundError(ProductServiceError):
    """Product not found exception."""
    
    def __init__(self, product_id: str):
        super().__init__(f"Product with ID {product_id} not found", 404)


class ProductAlreadyExistsError(ProductServiceError):
    """Product already exists exception."""
    
    def __init__(self, name: str):
        super().__init__(f"Product with name '{name}' already exists", 409)


class ValidationError(ProductServiceError):
    """Validation error exception."""
    
    def __init__(self, message: str, errors: dict = None):
        super().__init__(message, 400)
        self.errors = errors or {}


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(ProductServiceError)
    def handle_product_service_error(error: ProductServiceError):
        """Handle custom Product Service errors."""
        logger.error(
            "Product service error",
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
            if 'products_name_unique' in error_msg:
                return jsonify({
                    'error': 'Product name already exists',
                    'status_code': 409,
                    'details': {'field': 'name', 'message': 'This name is already taken'}
                }), 409
        
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