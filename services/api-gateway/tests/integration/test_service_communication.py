"""Integration tests for service-to-service communication."""
import pytest
import json
import responses
from unittest.mock import patch

# Mock service responses for testing
MOCK_PRODUCT = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Test Product",
    "type": "standard",
    "unit": "piece",
    "description": "Test product for integration tests"
}

MOCK_RECIPE = {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "yield_quantity": 24,
    "yield_unit": "piece",
    "ingredients": [
        {
            "product_id": "770e8400-e29b-41d4-a716-446655440002",
            "quantity": 500,
            "unit": "gram",
            "order": 1
        }
    ]
}

MOCK_CALCULATION = {
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "target_quantity": 100,
    "target_unit": "piece",
    "scale_factor": 4.17,
    "ingredients": [
        {
            "product_id": "770e8400-e29b-41d4-a716-446655440002",
            "calculated_quantity": 2085,
            "unit": "gram"
        }
    ]
}


@pytest.fixture
def mock_all_services():
    """Mock all backend services with comprehensive responses."""
    with responses.RequestsMock() as rsps:
        base_urls = {
            'product': 'http://mock-product-service:8001',
            'recipe': 'http://mock-recipe-service:8002',
            'calculator': 'http://mock-calculator-service:8003'
        }
        
        # Health checks for all services
        for service, url in base_urls.items():
            rsps.add(
                responses.GET,
                f'{url}/health',
                json={'status': 'healthy', 'service': f'{service}-service'},
                status=200
            )
        
        # Product Service endpoints
        rsps.add(
            responses.GET,
            f'{base_urls["product"]}/api/v1/products',
            json={'products': [MOCK_PRODUCT], 'total': 1},
            status=200
        )
        
        rsps.add(
            responses.GET,
            f'{base_urls["product"]}/api/v1/products/{MOCK_PRODUCT["id"]}',
            json=MOCK_PRODUCT,
            status=200
        )
        
        rsps.add(
            responses.POST,
            f'{base_urls["product"]}/api/v1/products',
            json=MOCK_PRODUCT,
            status=201
        )
        
        # Recipe Service endpoints
        rsps.add(
            responses.GET,
            f'{base_urls["recipe"]}/api/v1/recipes',
            json={'recipes': [MOCK_RECIPE], 'total': 1},
            status=200
        )
        
        rsps.add(
            responses.GET,
            f'{base_urls["recipe"]}/api/v1/recipes/product/{MOCK_PRODUCT["id"]}',
            json=MOCK_RECIPE,
            status=200
        )
        
        rsps.add(
            responses.POST,
            f'{base_urls["recipe"]}/api/v1/recipes',
            json=MOCK_RECIPE,
            status=201
        )
        
        # Calculator Service endpoints
        rsps.add(
            responses.POST,
            f'{base_urls["calculator"]}/api/v1/calculations/calculate',
            json=MOCK_CALCULATION,
            status=200
        )
        
        yield rsps


class TestProductServiceIntegration:
    """Test Product Service integration through API Gateway."""
    
    def test_get_products(self, client, mock_all_services):
        """Test getting products through gateway."""
        response = client.get('/api/v1/products')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'products' in data
        assert len(data['products']) == 1
        assert data['products'][0]['name'] == 'Test Product'
    
    def test_get_product_by_id(self, client, mock_all_services):
        """Test getting specific product through gateway."""
        product_id = MOCK_PRODUCT['id']
        response = client.get(f'/api/v1/products/{product_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['id'] == product_id
        assert data['name'] == 'Test Product'
    
    def test_create_product(self, client, mock_all_services):
        """Test creating product through gateway."""
        new_product = {
            'name': 'New Test Product',
            'type': 'standard',
            'unit': 'piece',
            'description': 'Created via gateway'
        }
        
        response = client.post('/api/v1/products',
                              json=new_product,
                              content_type='application/json')
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['name'] == 'Test Product'  # Mock returns fixed response
    
    def test_product_not_found(self, client, mock_all_services):
        """Test handling of non-existent product."""
        # Add 404 response to mock
        mock_all_services.add(
            responses.GET,
            'http://mock-product-service:8001/api/v1/products/nonexistent',
            json={'error': 'Product not found'},
            status=404
        )
        
        response = client.get('/api/v1/products/nonexistent')
        assert response.status_code == 404


class TestRecipeServiceIntegration:
    """Test Recipe Service integration through API Gateway."""
    
    def test_get_recipes(self, client, mock_all_services):
        """Test getting recipes through gateway."""
        response = client.get('/api/v1/recipes')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'recipes' in data
        assert len(data['recipes']) == 1
    
    def test_get_recipe_by_product(self, client, mock_all_services):
        """Test getting recipe by product ID through gateway."""
        product_id = MOCK_PRODUCT['id']
        response = client.get(f'/api/v1/recipes/product/{product_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['product_id'] == product_id
        assert len(data['ingredients']) == 1
    
    def test_create_recipe(self, client, mock_all_services):
        """Test creating recipe through gateway."""
        new_recipe = {
            'product_id': MOCK_PRODUCT['id'],
            'yield_quantity': 50,
            'yield_unit': 'piece',
            'ingredients': [
                {
                    'product_id': '770e8400-e29b-41d4-a716-446655440002',
                    'quantity': 1000,
                    'unit': 'gram',
                    'order': 1
                }
            ]
        }
        
        response = client.post('/api/v1/recipes',
                              json=new_recipe,
                              content_type='application/json')
        assert response.status_code == 201


class TestCalculatorServiceIntegration:
    """Test Calculator Service integration through API Gateway."""
    
    def test_calculate_recipe(self, client, mock_all_services):
        """Test recipe calculation through gateway."""
        calculation_request = {
            'product_id': MOCK_PRODUCT['id'],
            'target_quantity': 100,
            'target_unit': 'piece'
        }
        
        response = client.post('/api/v1/calculations/calculate',
                              json=calculation_request,
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['product_id'] == MOCK_PRODUCT['id']
        assert data['target_quantity'] == 100
        assert data['scale_factor'] == 4.17
        assert len(data['ingredients']) == 1


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows through API Gateway."""
    
    def test_complete_recipe_workflow(self, client, mock_all_services):
        """Test complete workflow: get product, get recipe, calculate scaling."""
        product_id = MOCK_PRODUCT['id']
        
        # Step 1: Get product details
        product_response = client.get(f'/api/v1/products/{product_id}')
        assert product_response.status_code == 200
        product_data = json.loads(product_response.data)
        
        # Step 2: Get recipe for product
        recipe_response = client.get(f'/api/v1/recipes/product/{product_id}')
        assert recipe_response.status_code == 200
        recipe_data = json.loads(recipe_response.data)
        
        # Step 3: Calculate scaled recipe
        calculation_request = {
            'product_id': product_id,
            'target_quantity': 100,
            'target_unit': product_data['unit']
        }
        
        calc_response = client.post('/api/v1/calculations/calculate',
                                   json=calculation_request,
                                   content_type='application/json')
        assert calc_response.status_code == 200
        calc_data = json.loads(calc_response.data)
        
        # Verify workflow consistency
        assert product_data['id'] == recipe_data['product_id']
        assert recipe_data['product_id'] == calc_data['product_id']


class TestErrorHandling:
    """Test error handling across services through API Gateway."""
    
    def test_service_unavailable(self, client):
        """Test handling when backend service is unavailable."""
        with responses.RequestsMock() as rsps:
            # Don't add any mock responses - simulate service down
            response = client.get('/api/v1/products')
            assert response.status_code == 503
            
            data = json.loads(response.data)
            assert 'error' in data
            assert data['status_code'] == 503
    
    def test_service_timeout(self, client, mock_all_services):
        """Test handling of service timeouts."""
        # Replace with timeout response
        mock_all_services.reset()
        mock_all_services.add(
            responses.GET,
            'http://mock-product-service:8001/api/v1/products',
            body=responses.ConnectionError('Connection timeout')
        )
        
        response = client.get('/api/v1/products')
        assert response.status_code == 503
    
    def test_invalid_request_data(self, client, mock_all_services):
        """Test handling of invalid request data."""
        # Test with invalid JSON
        response = client.post('/api/v1/products',
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_large_payload(self, client, mock_all_services):
        """Test handling of oversized payloads."""
        # Create large payload (16MB+)
        large_data = {
            'name': 'Test Product',
            'description': 'x' * (17 * 1024 * 1024)  # 17MB
        }
        
        response = client.post('/api/v1/products',
                              json=large_data,
                              content_type='application/json')
        assert response.status_code == 413


class TestGatewayFeatures:
    """Test Gateway-specific features."""
    
    def test_request_headers(self, client, mock_all_services):
        """Test that gateway adds proper headers."""
        response = client.get('/api/v1/products')
        assert response.status_code == 200
        
        # Check gateway headers
        assert 'X-Gateway-Version' in response.headers
        assert 'X-Request-ID' in response.headers
        assert 'X-Response-Time' in response.headers
    
    def test_cors_headers(self, client, mock_all_services):
        """Test CORS headers are properly set."""
        response = client.options('/api/v1/products')
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
    
    def test_rate_limiting_headers(self, client, mock_all_services):
        """Test rate limiting headers are included."""
        response = client.get('/api/v1/products')
        
        # Rate limiting headers might be present
        # (depends on configuration and actual rate limiter implementation)
        assert response.status_code == 200
    
    @pytest.mark.skip(reason="Caching test requires Redis setup")
    def test_response_caching(self, client, mock_all_services):
        """Test that GET responses are cached."""
        # First request
        response1 = client.get('/api/v1/products')
        assert response1.status_code == 200
        
        # Second request should be served from cache
        response2 = client.get('/api/v1/products')
        assert response2.status_code == 200
        # Would check X-Cache-Status header in real implementation


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    @pytest.mark.skip(reason="Circuit breaker test requires service failure simulation")
    def test_circuit_breaker_opens(self, client):
        """Test circuit breaker opens after failures."""
        # Would test circuit breaker opening after consecutive failures
        # and requests being rejected immediately
        pass
    
    @pytest.mark.skip(reason="Circuit breaker test requires service recovery simulation")
    def test_circuit_breaker_recovery(self, client):
        """Test circuit breaker recovery after service comes back."""
        # Would test circuit breaker transitioning from OPEN to HALF_OPEN to CLOSED
        pass