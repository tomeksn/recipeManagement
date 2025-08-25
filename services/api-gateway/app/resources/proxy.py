"""Request proxying resources for API Gateway."""
import re
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from flask import request, current_app, abort
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields

from ..services.service_client import service_client
from ..utils.exceptions import InvalidRequestError, ServiceUnavailableError

blp = Blueprint(
    'proxy',
    __name__,
    url_prefix='/api/v1',
    description='Service proxy endpoints'
)


class ProxyResponseSchema(Schema):
    """Generic proxy response schema."""
    # Allow additional unknown fields
    class Meta:
        unknown = 'INCLUDE'


def get_service_from_path(path: str) -> Optional[str]:
    """Determine target service from request path.
    
    Args:
        path: Request path
        
    Returns:
        Service name or None if no match
    """
    # Define routing patterns
    routing_patterns = {
        r'^/api/v1/products': 'product',
        r'^/api/v1/recipes': 'recipe', 
        r'^/api/v1/calculations': 'calculator'
    }
    
    for pattern, service in routing_patterns.items():
        if re.match(pattern, path):
            return service
    
    return None


def transform_path_for_service(path: str, service_name: str) -> str:
    """Transform request path for target service.
    
    Args:
        path: Original request path
        service_name: Target service name
        
    Returns:
        Transformed path for the service
    """
    # Remove gateway prefix and add service-specific path
    service_config = current_app.config['SERVICES'].get(service_name, {})
    service_prefix = service_config.get('prefix', '')
    
    # For now, pass through the path as-is since services expect full paths
    return path


def validate_request_size():
    """Validate request payload size."""
    max_length = current_app.config.get('MAX_CONTENT_LENGTH')
    if max_length and request.content_length and request.content_length > max_length:
        raise InvalidRequestError(
            f"Request payload too large. Maximum allowed: {max_length} bytes"
        )


def get_forwarded_headers() -> Dict[str, str]:
    """Get headers to forward to backend services."""
    # Headers to forward
    forward_headers = [
        'Authorization',
        'Content-Type',
        'Accept',
        'Accept-Language',
        'User-Agent',
        'X-Request-ID',
        'X-Correlation-ID'
    ]
    
    headers = {}
    for header in forward_headers:
        value = request.headers.get(header)
        if value:
            headers[header] = value
    
    # Add gateway identification
    headers['X-Forwarded-By'] = 'recipe-management-gateway'
    headers['X-Forwarded-For'] = request.remote_addr
    headers['X-Original-Path'] = request.path
    
    return headers


@blp.route('/products/', methods=['GET', 'POST'])
@blp.route('/products', methods=['GET', 'POST'])
@blp.route('/products/<path:resource_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
class ProductProxy(MethodView):
    """Proxy for Product Service endpoints."""
    
    @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def get(self, resource_path: str = ''):
        """Proxy GET requests to Product Service."""
        return self._proxy_request('product', resource_path)
    
    @blp.alt_response(400, description="Invalid request")
    @blp.alt_response(503, description="Service unavailable")
    def post(self, resource_path: str = ''):
        """Proxy POST requests to Product Service."""
        return self._proxy_request('product', resource_path)
    
    @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def put(self, resource_path: str = ''):
        """Proxy PUT requests to Product Service."""
        return self._proxy_request('product', resource_path)
    
    @blp.response(204)
    @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def delete(self, resource_path: str = ''):
        """Proxy DELETE requests to Product Service."""
        return self._proxy_request('product', resource_path)
    
    def _proxy_request(self, service_name: str, resource_path: str):
        """Common proxy logic."""
        validate_request_size()
        
        # Build target endpoint
        endpoint = "/api/v1/products/"
        if resource_path:
            endpoint += resource_path
        
        # Get request data
        json_data = None
        if request.is_json and request.get_json():
            json_data = request.get_json()
        
        # Forward request
        headers = get_forwarded_headers()
        
        try:
            if request.method == 'GET':
                result = service_client.get(
                    service_name, endpoint, 
                    params=request.args.to_dict(),
                    headers=headers,
                    use_cache=False  # Disable cache for debugging
                )
                # Debug logging
                current_app.logger.info(f"DEBUG: ProductProxy result type: {type(result)}, Result: {result}")
            elif request.method == 'POST':
                result = service_client.post(
                    service_name, endpoint,
                    json_data=json_data,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'PUT':
                result = service_client.put(
                    service_name, endpoint,
                    json_data=json_data,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'DELETE':
                result = service_client.delete(
                    service_name, endpoint,
                    params=request.args.to_dict(),
                    headers=headers
                )
            else:
                raise InvalidRequestError(f"Method {request.method} not supported")
            
            if result is None:
                abort(404, description="Resource not found")
            
            return result
            
        except ServiceUnavailableError as e:
            current_app.logger.error(f"Service unavailable: {str(e)}")
            abort(503, description=str(e))
        except Exception as e:
            current_app.logger.error(f"Proxy error: {str(e)}")
            abort(500, description="Internal gateway error")


@blp.route('/recipes/', methods=['GET', 'POST'])
@blp.route('/recipes', methods=['GET', 'POST'])
@blp.route('/recipes/<path:resource_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
class RecipeProxy(MethodView):
    """Proxy for Recipe Service endpoints."""
    
    @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def get(self, resource_path: str = ''):
        """Proxy GET requests to Recipe Service."""
        return self._proxy_request('recipe', resource_path)
    
        @blp.alt_response(400, description="Invalid request")
    @blp.alt_response(503, description="Service unavailable")
    def post(self, resource_path: str = ''):
        """Proxy POST requests to Recipe Service."""
        return self._proxy_request('recipe', resource_path)
    
        @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def put(self, resource_path: str = ''):
        """Proxy PUT requests to Recipe Service."""
        return self._proxy_request('recipe', resource_path)
    
    @blp.response(204)
    @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def delete(self, resource_path: str = ''):
        """Proxy DELETE requests to Recipe Service."""
        return self._proxy_request('recipe', resource_path)
    
    def _proxy_request(self, service_name: str, resource_path: str):
        """Common proxy logic for recipes."""
        validate_request_size()
        
        # Build target endpoint
        endpoint = "/api/v1/recipes/"
        if resource_path:
            endpoint += resource_path
        
        # Get request data
        json_data = None
        if request.is_json and request.get_json():
            json_data = request.get_json()
        
        # Forward request
        headers = get_forwarded_headers()
        
        try:
            if request.method == 'GET':
                result = service_client.get(
                    service_name, endpoint,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'POST':
                result = service_client.post(
                    service_name, endpoint,
                    json_data=json_data,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'PUT':
                result = service_client.put(
                    service_name, endpoint,
                    json_data=json_data,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'DELETE':
                result = service_client.delete(
                    service_name, endpoint,
                    params=request.args.to_dict(),
                    headers=headers
                )
            else:
                raise InvalidRequestError(f"Method {request.method} not supported")
            
            if result is None:
                abort(404, description="Resource not found")
            
            return result
            
        except ServiceUnavailableError as e:
            current_app.logger.error(f"Service unavailable: {str(e)}")
            abort(503, description=str(e))
        except Exception as e:
            current_app.logger.error(f"Proxy error: {str(e)}")
            abort(500, description="Internal gateway error")


@blp.route('/calculations', methods=['GET', 'POST'])
@blp.route('/calculations/<path:resource_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
class CalculatorProxy(MethodView):
    """Proxy for Calculator Service endpoints."""
    
        @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def get(self, resource_path: str = ''):
        """Proxy GET requests to Calculator Service."""
        return self._proxy_request('calculator', resource_path)
    
        @blp.alt_response(400, description="Invalid request")
    @blp.alt_response(503, description="Service unavailable")
    def post(self, resource_path: str = ''):
        """Proxy POST requests to Calculator Service."""
        return self._proxy_request('calculator', resource_path)
    
        @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def put(self, resource_path: str = ''):
        """Proxy PUT requests to Calculator Service."""
        return self._proxy_request('calculator', resource_path)
    
    @blp.response(204)
    @blp.alt_response(404, description="Resource not found")
    @blp.alt_response(503, description="Service unavailable")
    def delete(self, resource_path: str = ''):
        """Proxy DELETE requests to Calculator Service."""
        return self._proxy_request('calculator', resource_path)
    
    def _proxy_request(self, service_name: str, resource_path: str):
        """Common proxy logic for calculations."""
        validate_request_size()
        
        # Build target endpoint
        endpoint = f"/api/v1/calculations"
        if resource_path:
            endpoint += f"/{resource_path}"
        
        # Get request data
        json_data = None
        if request.is_json and request.get_json():
            json_data = request.get_json()
        
        # Forward request
        headers = get_forwarded_headers()
        
        try:
            if request.method == 'GET':
                result = service_client.get(
                    service_name, endpoint,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'POST':
                result = service_client.post(
                    service_name, endpoint,
                    json_data=json_data,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'PUT':
                result = service_client.put(
                    service_name, endpoint,
                    json_data=json_data,
                    params=request.args.to_dict(),
                    headers=headers
                )
            elif request.method == 'DELETE':
                result = service_client.delete(
                    service_name, endpoint,
                    params=request.args.to_dict(),
                    headers=headers
                )
            else:
                raise InvalidRequestError(f"Method {request.method} not supported")
            
            if result is None:
                abort(404, description="Resource not found")
            
            return result
            
        except ServiceUnavailableError as e:
            current_app.logger.error(f"Service unavailable: {str(e)}")
            abort(503, description=str(e))
        except Exception as e:
            current_app.logger.error(f"Proxy error: {str(e)}")
            abort(500, description="Internal gateway error")