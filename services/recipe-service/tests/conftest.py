"""Pytest configuration and fixtures for Recipe Service tests."""
import pytest
from unittest.mock import Mock, patch
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('TestingConfig')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'PRODUCT_SERVICE_URL': 'http://mock-product-service'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def mock_product_client():
    """Mock Product Service client."""
    with patch('app.services.product_client.product_client') as mock:
        # Configure default mock responses
        mock.get_product.return_value = {
            'id': 'test-product-id',
            'name': 'Test Product',
            'type': 'standard',
            'unit': 'piece',
            'description': 'Test product description'
        }
        mock.validate_product_exists.return_value = True
        mock.health_check.return_value = True
        yield mock