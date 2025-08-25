"""Custom exceptions for Calculator Service."""
from typing import Dict, Any, Optional
from flask import Flask, jsonify


class CalculatorServiceError(Exception):
    """Base exception for Calculator Service."""
    
    def __init__(self, message: str, status_code: int = 500, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


class CalculationError(CalculatorServiceError):
    """Exception raised for calculation errors."""
    
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, payload=payload)


class InvalidScaleFactorError(CalculationError):
    """Exception raised for invalid scale factors."""
    pass


class RecipeNotFoundError(CalculatorServiceError):
    """Exception raised when recipe is not found."""
    
    def __init__(self, recipe_id: str):
        message = f"Recipe with ID {recipe_id} not found"
        super().__init__(message, status_code=404)


class RecipeServiceError(CalculatorServiceError):
    """Exception raised for Recipe Service communication errors."""
    
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message, status_code=status_code)


class InvalidInputError(CalculationError):
    """Exception raised for invalid input data."""
    pass


class MaxIngredientsExceededError(CalculationError):
    """Exception raised when too many ingredients in calculation."""
    
    def __init__(self, max_ingredients: int):
        message = f"Too many ingredients in calculation. Maximum allowed: {max_ingredients}"
        super().__init__(message)


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(CalculatorServiceError)
    def handle_calculator_service_error(error: CalculatorServiceError):
        """Handle Calculator Service specific errors."""
        response = {
            'error': error.message,
            'status_code': error.status_code
        }
        
        if error.payload:
            response['details'] = error.payload
            
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Resource not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            'error': 'Method not allowed',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle 500 errors."""
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500