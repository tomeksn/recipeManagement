"""Custom exceptions for API Gateway."""
from typing import Dict, Any, Optional
from flask import Flask, jsonify


class GatewayError(Exception):
    """Base exception for API Gateway."""
    
    def __init__(self, message: str, status_code: int = 500, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}


class ServiceUnavailableError(GatewayError):
    """Exception raised when a backend service is unavailable."""
    
    def __init__(self, service_name: str, details: Optional[str] = None):
        message = f"Service '{service_name}' is currently unavailable"
        if details:
            message += f": {details}"
        super().__init__(message, status_code=503)
        self.service_name = service_name


class ServiceTimeoutError(GatewayError):
    """Exception raised when a backend service times out."""
    
    def __init__(self, service_name: str, timeout: int):
        message = f"Service '{service_name}' timed out after {timeout} seconds"
        super().__init__(message, status_code=504)
        self.service_name = service_name
        self.timeout = timeout


class ServiceAuthenticationError(GatewayError):
    """Exception raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class ServiceAuthorizationError(GatewayError):
    """Exception raised for authorization failures."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class RateLimitExceededError(GatewayError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, limit: str, reset_time: Optional[int] = None):
        message = f"Rate limit exceeded: {limit}"
        super().__init__(message, status_code=429)
        self.limit = limit
        self.reset_time = reset_time


class InvalidRequestError(GatewayError):
    """Exception raised for invalid requests."""
    
    def __init__(self, message: str, validation_errors: Optional[Dict] = None):
        super().__init__(message, status_code=400)
        if validation_errors:
            self.payload['validation_errors'] = validation_errors


class UpstreamServiceError(GatewayError):
    """Exception raised when upstream service returns an error."""
    
    def __init__(self, service_name: str, status_code: int, message: str, 
                 upstream_response: Optional[Dict] = None):
        super().__init__(f"Upstream service error from {service_name}: {message}", status_code)
        self.service_name = service_name
        self.upstream_response = upstream_response


class CircuitBreakerOpenError(GatewayError):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, service_name: str):
        message = f"Circuit breaker is open for service '{service_name}'"
        super().__init__(message, status_code=503)
        self.service_name = service_name


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(GatewayError)
    def handle_gateway_error(error: GatewayError):
        """Handle API Gateway specific errors."""
        response = {
            'error': error.message,
            'status_code': error.status_code,
            'timestamp': app.extensions.get('current_request_time'),
            'service': 'api-gateway'
        }
        
        if error.payload:
            response['details'] = error.payload
            
        # Add specific headers for certain error types
        headers = {}
        if isinstance(error, RateLimitExceededError) and error.reset_time:
            headers['Retry-After'] = str(error.reset_time)
            
        return jsonify(response), error.status_code, headers
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Endpoint not found',
            'status_code': 404,
            'service': 'api-gateway',
            'message': 'The requested endpoint does not exist'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({
            'error': 'Method not allowed',
            'status_code': 405,
            'service': 'api-gateway',
            'message': 'The request method is not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(413)
    def handle_payload_too_large(error):
        """Handle 413 errors."""
        return jsonify({
            'error': 'Payload too large',
            'status_code': 413,
            'service': 'api-gateway',
            'message': 'Request payload exceeds maximum allowed size'
        }), 413
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle 500 errors."""
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500,
            'service': 'api-gateway',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(502)
    def handle_bad_gateway(error):
        """Handle 502 errors."""
        return jsonify({
            'error': 'Bad gateway',
            'status_code': 502,
            'service': 'api-gateway',
            'message': 'Received invalid response from upstream service'
        }), 502
    
    @app.errorhandler(503)
    def handle_service_unavailable(error):
        """Handle 503 errors."""
        return jsonify({
            'error': 'Service unavailable',
            'status_code': 503,
            'service': 'api-gateway',
            'message': 'Service is temporarily unavailable'
        }), 503
    
    @app.errorhandler(504)
    def handle_gateway_timeout(error):
        """Handle 504 errors."""
        return jsonify({
            'error': 'Gateway timeout',
            'status_code': 504,
            'service': 'api-gateway',
            'message': 'Upstream service did not respond in time'
        }), 504