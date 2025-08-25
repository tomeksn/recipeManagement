"""Pytest configuration and fixtures for Product Service tests."""
import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('TestingConfig')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
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