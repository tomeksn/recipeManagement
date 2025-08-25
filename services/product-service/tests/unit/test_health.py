"""Unit tests for health check endpoint."""
import pytest
from flask import json


def test_health_endpoint(client):
    """Test health check endpoint returns success."""
    response = client.get('/health')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'product-service'