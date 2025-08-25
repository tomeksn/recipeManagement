"""Pytest configuration and fixtures for Calculator Service tests."""
import pytest
from unittest.mock import Mock, MagicMock
from flask import Flask

from app import create_app
from app.extensions import cache


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    # Override configuration for testing
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'REDIS_URL': 'redis://localhost:6379/15',  # Test database
        'CACHE_TTL': 0,  # Disable caching in tests
        'CALCULATION_CACHE_TTL': 0,
        'ENABLE_RESULT_CACHING': False,
        'RECIPE_SERVICE_URL': 'http://mock-recipe-service',
        'RECIPE_SERVICE_TIMEOUT': 5,
        'RECIPE_SERVICE_RETRIES': 1,
        'PRECISION_DECIMAL_PLACES': 3,
        'MAX_SCALE_FACTOR': 1000.0,
        'MIN_SCALE_FACTOR': 0.001,
        'MAX_INGREDIENTS_PER_CALCULATION': 1000
    })
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Create application context."""
    with app.app_context():
        yield app


@pytest.fixture
def mock_recipe_client():
    """Mock recipe client for testing."""
    mock_client = Mock()
    
    # Mock health check
    mock_client.health_check.return_value = True
    
    # Mock recipe data
    mock_recipe = {
        'id': '550e8400-e29b-41d4-a716-446655440000',
        'product': {
            'id': '550e8400-e29b-41d4-a716-446655440000',
            'name': 'Test Recipe',
            'type': 'standard',
            'unit': 'piece'
        },
        'yield_quantity': 24,
        'yield_unit': 'piece',
        'ingredients': [
            {
                'product_id': '660e8400-e29b-41d4-a716-446655440001',
                'product_name': 'Flour',
                'quantity': 500,
                'unit': 'gram',
                'order': 1
            },
            {
                'product_id': '660e8400-e29b-41d4-a716-446655440002',
                'product_name': 'Sugar',
                'quantity': 200,
                'unit': 'gram',
                'order': 2
            }
        ]
    }
    
    mock_client.get_recipe.return_value = mock_recipe
    mock_client.get_recipe_hierarchy.return_value = mock_recipe
    mock_client.get_multiple_recipes.return_value = {
        '550e8400-e29b-41d4-a716-446655440000': mock_recipe
    }
    
    return mock_client


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing."""
    return {
        'id': '550e8400-e29b-41d4-a716-446655440000',
        'product': {
            'id': '550e8400-e29b-41d4-a716-446655440000',
            'name': 'Chocolate Chip Cookies',
            'type': 'standard',
            'unit': 'piece'
        },
        'yield_quantity': 24,
        'yield_unit': 'piece',
        'ingredients': [
            {
                'product_id': '660e8400-e29b-41d4-a716-446655440001',
                'product_name': 'Flour',
                'quantity': 500,
                'unit': 'gram',
                'order': 1
            },
            {
                'product_id': '660e8400-e29b-41d4-a716-446655440002',
                'product_name': 'Sugar',
                'quantity': 200,
                'unit': 'gram',
                'order': 2
            },
            {
                'product_id': '660e8400-e29b-41d4-a716-446655440003',
                'product_name': 'Chocolate Chips',
                'quantity': 300,
                'unit': 'gram',
                'order': 3
            },
            {
                'product_id': '660e8400-e29b-41d4-a716-446655440004',
                'product_name': 'Eggs',
                'quantity': 2,
                'unit': 'piece',
                'order': 4
            }
        ]
    }


@pytest.fixture
def hierarchical_recipe_data():
    """Sample hierarchical recipe data for testing."""
    return {
        'id': '770e8400-e29b-41d4-a716-446655440000',
        'product': {
            'id': '770e8400-e29b-41d4-a716-446655440000',
            'name': 'Cake Mix',
            'type': 'semi-product',
            'unit': 'gram'
        },
        'yield_quantity': 1000,
        'yield_unit': 'gram',
        'ingredients': [
            {
                'product_id': '660e8400-e29b-41d4-a716-446655440001',
                'product_name': 'Flour',
                'quantity': 600,
                'unit': 'gram',
                'order': 1
            },
            {
                'product_id': '770e8400-e29b-41d4-a716-446655440001',  # Semi-product
                'product_name': 'Sugar Mix',
                'quantity': 400,
                'unit': 'gram',
                'order': 2
            }
        ]
    }


@pytest.fixture
def calculation_request():
    """Sample calculation request for testing."""
    return {
        'product_id': '550e8400-e29b-41d4-a716-446655440000',
        'target_quantity': 100,
        'target_unit': 'piece',
        'include_hierarchy': False,
        'max_depth': 5,
        'precision': 3
    }


@pytest.fixture
def batch_calculation_request():
    """Sample batch calculation request for testing."""
    return {
        'calculations': [
            {
                'product_id': '550e8400-e29b-41d4-a716-446655440000',
                'target_quantity': 100,
                'target_unit': 'piece',
                'include_hierarchy': False,
                'max_depth': 5
            },
            {
                'product_id': '550e8400-e29b-41d4-a716-446655440000',
                'target_quantity': 50,
                'target_unit': 'piece',
                'include_hierarchy': True,
                'max_depth': 3
            }
        ]
    }


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    try:
        cache.clear()
    except:
        pass  # Cache might not be initialized
    yield
    try:
        cache.clear()
    except:
        pass