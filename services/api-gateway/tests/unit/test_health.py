"""Unit tests for health check endpoints."""
import pytest
import json


def test_root_health_check(client, mock_services):
    """Test root health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['service'] == 'api-gateway'
    assert 'status' in data
    assert 'version' in data


def test_detailed_health_check(client, mock_services):
    """Test detailed health check endpoint."""
    response = client.get('/health/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['service'] == 'api-gateway'
    assert 'dependencies' in data
    assert 'gateway_info' in data


def test_readiness_check(client, mock_services):
    """Test readiness check endpoint."""
    response = client.get('/health/ready')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['service'] == 'api-gateway'
    assert data['status'] in ['ready', 'not_ready']


def test_liveness_check(client):
    """Test liveness check endpoint."""
    response = client.get('/health/live')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['service'] == 'api-gateway'
    assert data['status'] == 'alive'


def test_services_health(client, mock_services):
    """Test services health endpoint."""
    response = client.get('/health/services')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'services' in data