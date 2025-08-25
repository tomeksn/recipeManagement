"""Unit tests for health check endpoint."""
import pytest
from flask import json


def test_health_endpoint_success(client, mock_product_client):
    """Test health check endpoint returns success."""
    response = client.get('/health')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] in ['healthy', 'degraded']
    assert data['service'] == 'recipe-service'
    assert 'dependencies' in data


def test_health_endpoint_product_service_down(client):
    """Test health check when Product Service is down."""
    with pytest.mock.patch('app.services.product_client.product_client') as mock_client:
        mock_client.health_check.return_value = False
        
        response = client.get('/health')
        
        assert response.status_code == 200  # Still returns 200 but degraded
        
        data = json.loads(response.data)
        assert data['status'] == 'degraded'
        assert data['dependencies']['product_service'] == 'disconnected'