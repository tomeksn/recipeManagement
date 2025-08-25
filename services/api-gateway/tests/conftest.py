"""Test configuration and fixtures for API Gateway."""
import pytest
import responses
from app import create_app


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app('testing')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def mock_services():
    """Mock backend services."""
    with responses.RequestsMock() as rsps:
        # Mock Product Service health
        rsps.add(
            responses.GET,
            'http://mock-product-service:8001/health',
            json={'status': 'healthy', 'service': 'product-service'},
            status=200
        )
        
        # Mock Recipe Service health
        rsps.add(
            responses.GET,
            'http://mock-recipe-service:8002/health',
            json={'status': 'healthy', 'service': 'recipe-service'},
            status=200
        )
        
        # Mock Calculator Service health
        rsps.add(
            responses.GET,
            'http://mock-calculator-service:8003/health',
            json={'status': 'healthy', 'service': 'calculator-service'},
            status=200
        )
        
        yield rsps