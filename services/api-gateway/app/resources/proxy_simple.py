"""Simple proxy without Flask-SMOREST schemas."""
from flask import Blueprint, request, jsonify, current_app
from ..services.service_client import service_client

# Create simple blueprint
proxy_bp = Blueprint('proxy', __name__, url_prefix='/api/v1')

@proxy_bp.route('/products/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@proxy_bp.route('/products', methods=['GET', 'POST', 'PUT', 'DELETE'])
@proxy_bp.route('/products/<path:resource_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def product_proxy(resource_path=''):
    """Proxy for Product Service."""
    endpoint = "/api/v1/products/"
    if resource_path:
        endpoint += resource_path
    
    headers = {}
    for header in ['Authorization', 'Content-Type', 'Accept']:
        value = request.headers.get(header)
        if value:
            headers[header] = value
    
    try:
        if request.method == 'GET':
            result = service_client.get(
                'product', endpoint,
                params=request.args.to_dict(),
                headers=headers,
                use_cache=False
            )
        elif request.method == 'POST':
            result = service_client.post(
                'product', endpoint,
                json_data=request.get_json(),
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'PUT':
            result = service_client.put(
                'product', endpoint,
                json_data=request.get_json(),
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'DELETE':
            result = service_client.delete(
                'product', endpoint,
                params=request.args.to_dict(),
                headers=headers
            )
        
        current_app.logger.info(f"DEBUG: Proxy result: {type(result)}")
        return jsonify(result) if result else ('', 404)
        
    except Exception as e:
        current_app.logger.error(f"Proxy error: {str(e)}")
        return jsonify({'error': str(e)}), 503


@proxy_bp.route('/recipes/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@proxy_bp.route('/recipes', methods=['GET', 'POST', 'PUT', 'DELETE'])
@proxy_bp.route('/recipes/<path:resource_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def recipe_proxy(resource_path=''):
    """Proxy for Recipe Service."""
    endpoint = "/api/v1/recipes/"
    if resource_path:
        endpoint += resource_path
    
    headers = {}
    for header in ['Authorization', 'Content-Type', 'Accept']:
        value = request.headers.get(header)
        if value:
            headers[header] = value
    
    try:
        if request.method == 'GET':
            result = service_client.get(
                'recipe', endpoint,
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'POST':
            result = service_client.post(
                'recipe', endpoint,
                json_data=request.get_json(),
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'PUT':
            result = service_client.put(
                'recipe', endpoint,
                json_data=request.get_json(),
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'DELETE':
            result = service_client.delete(
                'recipe', endpoint,
                params=request.args.to_dict(),
                headers=headers
            )
        
        return jsonify(result) if result else ('', 404)
        
    except Exception as e:
        current_app.logger.error(f"Recipe proxy error: {str(e)}")
        return jsonify({'error': str(e)}), 503


@proxy_bp.route('/calculations', methods=['GET', 'POST', 'PUT', 'DELETE'])
@proxy_bp.route('/calculations/<path:resource_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def calculator_proxy(resource_path=''):
    """Proxy for Calculator Service."""
    endpoint = "/api/v1/calculations"
    if resource_path:
        endpoint += f"/{resource_path}"
    
    headers = {}
    for header in ['Authorization', 'Content-Type', 'Accept']:
        value = request.headers.get(header)
        if value:
            headers[header] = value
    
    try:
        if request.method == 'GET':
            result = service_client.get(
                'calculator', endpoint,
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'POST':
            result = service_client.post(
                'calculator', endpoint,
                json_data=request.get_json(),
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'PUT':
            result = service_client.put(
                'calculator', endpoint,
                json_data=request.get_json(),
                params=request.args.to_dict(),
                headers=headers
            )
        elif request.method == 'DELETE':
            result = service_client.delete(
                'calculator', endpoint,
                params=request.args.to_dict(),
                headers=headers
            )
        
        return jsonify(result) if result else ('', 404)
        
    except Exception as e:
        current_app.logger.error(f"Calculator proxy error: {str(e)}")
        return jsonify({'error': str(e)}), 503


@proxy_bp.route('/auth/login', methods=['POST'])
def auth_login():
    """Temporary mock login endpoint."""
    # Mock response for frontend testing - matching TokenResponse type
    return jsonify({
        'access_token': 'mock-jwt-token-for-testing',
        'refresh_token': 'mock-refresh-token-for-testing',
        'token_type': 'Bearer',
        'expires_in': 3600,
        'user': {
            'id': 'mock-user-123',
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'admin',
            'avatar': None,
            'created_at': '2025-01-01T00:00:00Z',
            'last_login': '2025-08-22T14:00:00Z'
        }
    })


@proxy_bp.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Temporary mock logout endpoint."""
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@proxy_bp.route('/auth/me', methods=['GET'])
def auth_me():
    """Temporary mock current user endpoint."""
    # Mock current user response
    return jsonify({
        'id': 'mock-user-123',
        'name': 'Test User',
        'email': 'test@example.com',
        'role': 'admin',
        'avatar': None,
        'created_at': '2025-01-01T00:00:00Z',
        'last_login': '2025-08-22T14:00:00Z'
    })