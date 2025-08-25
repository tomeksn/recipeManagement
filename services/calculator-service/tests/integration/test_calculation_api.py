"""Integration tests for Calculator Service API endpoints."""
import pytest
import json
from unittest.mock import patch

from app.services.recipe_client import recipe_client


class TestCalculationAPI:
    """Test calculation API endpoints."""
    
    @patch.object(recipe_client, 'get_recipe')
    def test_calculate_endpoint_success(self, mock_get_recipe, client, sample_recipe_data):
        """Test successful calculation via API."""
        mock_get_recipe.return_value = sample_recipe_data
        
        request_data = {
            'product_id': '550e8400-e29b-41d4-a716-446655440000',
            'target_quantity': 100,
            'target_unit': 'piece',
            'include_hierarchy': False,
            'max_depth': 5,
            'precision': 3
        }
        
        response = client.post(
            '/api/v1/calculations/calculate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['product_id'] == '550e8400-e29b-41d4-a716-446655440000'
        assert data['target_quantity'] == 100
        assert data['target_unit'] == 'piece'
        assert abs(data['scale_factor'] - 4.166666666666667) < 0.000001
        assert len(data['ingredients']) == 4
        assert 'calculation_time_ms' in data
        assert 'calculation_metadata' in data
    
    @patch.object(recipe_client, 'get_recipe')
    def test_calculate_endpoint_recipe_not_found(self, mock_get_recipe, client):
        """Test calculation with non-existent recipe."""
        mock_get_recipe.return_value = None
        
        request_data = {
            'product_id': 'nonexistent-id',
            'target_quantity': 100,
            'target_unit': 'piece'
        }
        
        response = client.post(
            '/api/v1/calculations/calculate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_calculate_endpoint_invalid_request(self, client):
        """Test calculation with invalid request data."""
        request_data = {
            'product_id': 'invalid-uuid',  # Invalid UUID
            'target_quantity': -10,  # Negative quantity
            'target_unit': 'invalid_unit'  # Invalid unit
        }
        
        response = client.post(
            '/api/v1/calculations/calculate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_calculate_endpoint_missing_fields(self, client):
        """Test calculation with missing required fields."""
        request_data = {
            'target_quantity': 100
            # Missing product_id and target_unit
        }
        
        response = client.post(
            '/api/v1/calculations/calculate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 422
    
    @patch.object(recipe_client, 'get_recipe')
    def test_calculate_endpoint_with_hierarchy(self, mock_get_recipe, client, hierarchical_recipe_data):
        """Test calculation with hierarchy expansion."""
        # Mock hierarchical recipe data
        mock_get_recipe.side_effect = [
            hierarchical_recipe_data,  # Main recipe
            {  # Sub-recipe for Sugar Mix
                'id': '770e8400-e29b-41d4-a716-446655440001',
                'product': {
                    'id': '770e8400-e29b-41d4-a716-446655440001',
                    'name': 'Sugar Mix',
                    'type': 'semi-product',
                    'unit': 'gram'
                },
                'yield_quantity': 400,
                'yield_unit': 'gram',
                'ingredients': [
                    {
                        'product_id': '660e8400-e29b-41d4-a716-446655440002',
                        'product_name': 'White Sugar',
                        'quantity': 300,
                        'unit': 'gram',
                        'order': 1
                    },
                    {
                        'product_id': '660e8400-e29b-41d4-a716-446655440003',
                        'product_name': 'Brown Sugar',
                        'quantity': 100,
                        'unit': 'gram',
                        'order': 2
                    }
                ]
            }
        ]
        
        request_data = {
            'product_id': '770e8400-e29b-41d4-a716-446655440000',
            'target_quantity': 500,
            'target_unit': 'gram',
            'include_hierarchy': True,
            'max_depth': 3
        }
        
        response = client.post(
            '/api/v1/calculations/calculate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['scale_factor'] == 0.5
        assert data['calculation_metadata']['include_hierarchy'] is True
        
        # Check for hierarchical expansion
        sugar_mix = next(
            (ing for ing in data['ingredients'] if ing['product_name'] == 'Sugar Mix'),
            None
        )
        assert sugar_mix is not None
        # Note: Full hierarchy testing would require more complex mocking
    
    @patch.object(recipe_client, 'get_recipe')
    def test_batch_calculate_endpoint(self, mock_get_recipe, client, sample_recipe_data):
        """Test batch calculation endpoint."""
        mock_get_recipe.return_value = sample_recipe_data
        
        request_data = {
            'calculations': [
                {
                    'product_id': '550e8400-e29b-41d4-a716-446655440000',
                    'target_quantity': 100,
                    'target_unit': 'piece'
                },
                {
                    'product_id': '550e8400-e29b-41d4-a716-446655440000',
                    'target_quantity': 50,
                    'target_unit': 'piece'
                }
            ]
        }
        
        response = client.post(
            '/api/v1/calculations/calculate/batch',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'results' in data
        assert 'summary' in data
        assert data['summary']['total_requests'] == 2
        assert data['summary']['successful'] == 2
        assert len(data['results']) == 2
    
    def test_batch_calculate_empty_request(self, client):
        """Test batch calculation with empty request."""
        request_data = {
            'calculations': []
        }
        
        response = client.post(
            '/api/v1/calculations/calculate/batch',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 422  # Validation error for empty list
    
    def test_batch_calculate_too_many_requests(self, client):
        """Test batch calculation with too many requests."""
        request_data = {
            'calculations': [
                {
                    'product_id': '550e8400-e29b-41d4-a716-446655440000',
                    'target_quantity': 100,
                    'target_unit': 'piece'
                }
            ] * 51  # Exceeds maximum of 50
        }
        
        response = client.post(
            '/api/v1/calculations/calculate/batch',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 422
    
    def test_calculation_history_endpoint(self, client):
        """Test calculation history endpoint."""
        response = client.get('/api/v1/calculations/history')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_calculation_history_with_filters(self, client):
        """Test calculation history with query parameters."""
        response = client.get(
            '/api/v1/calculations/history?product_id=550e8400-e29b-41d4-a716-446655440000&limit=10&offset=5'
        )
        
        assert response.status_code == 200
    
    def test_cache_stats_endpoint(self, client):
        """Test cache statistics endpoint."""
        response = client.get('/api/v1/calculations/cache/stats')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_keys' in data
        assert 'hit_rate' in data
        assert 'memory_usage' in data
    
    def test_cache_clear_endpoint(self, client):
        """Test cache clear endpoint."""
        request_data = {
            'confirm': True
        }
        
        response = client.post(
            '/api/v1/calculations/cache/clear',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'cleared_keys' in data
        assert 'message' in data
    
    def test_cache_clear_without_confirmation(self, client):
        """Test cache clear without confirmation."""
        request_data = {
            'confirm': False
        }
        
        response = client.post(
            '/api/v1/calculations/cache/clear',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @patch.object(recipe_client, 'health_check')
    def test_health_endpoint_healthy(self, mock_health, client):
        """Test health endpoint when all dependencies are healthy."""
        mock_health.return_value = True
        
        response = client.get('/api/v1/health/')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] in ['healthy', 'degraded']
        assert data['service'] == 'calculator-service'
        assert 'dependencies' in data
    
    @patch.object(recipe_client, 'health_check')
    def test_health_endpoint_degraded(self, mock_health, client):
        """Test health endpoint when dependencies are unhealthy."""
        mock_health.return_value = False
        
        response = client.get('/api/v1/health/')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'degraded'
        assert data['dependencies']['recipe_service'] == 'disconnected'
    
    def test_readiness_endpoint(self, client):
        """Test readiness endpoint."""
        response = client.get('/api/v1/health/ready')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ready'
        assert data['service'] == 'calculator-service'
    
    def test_liveness_endpoint(self, client):
        """Test liveness endpoint."""
        response = client.get('/api/v1/health/live')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'alive'
        assert data['service'] == 'calculator-service'
    
    def test_root_health_endpoint(self, client):
        """Test root health endpoint."""
        response = client.get('/health')
        
        assert response.status_code in [200, 503]  # Might fail if Redis not available


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_json(self, client):
        """Test request with invalid JSON."""
        response = client.post(
            '/api/v1/calculations/calculate',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """Test request without content type."""
        request_data = {
            'product_id': '550e8400-e29b-41d4-a716-446655440000',
            'target_quantity': 100,
            'target_unit': 'piece'
        }
        
        response = client.post(
            '/api/v1/calculations/calculate',
            data=json.dumps(request_data)
            # No content_type specified
        )
        
        # Should still work with application/json detection
        assert response.status_code in [200, 400, 422]
    
    def test_nonexistent_endpoint(self, client):
        """Test request to non-existent endpoint."""
        response = client.get('/api/v1/nonexistent')
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed on endpoint."""
        response = client.delete('/api/v1/calculations/calculate')
        
        assert response.status_code == 405