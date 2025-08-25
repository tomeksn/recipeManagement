"""Integration tests for Search API endpoints."""
import pytest
import json
import uuid

from app.models.product import Product, ProductType, ProductUnit
from app.extensions import db


class TestAdvancedSearchAPI:
    """Test cases for Advanced Search API endpoints."""
    
    def test_advanced_search_basic(self, client, app):
        """Test basic advanced search functionality."""
        with app.app_context():
            db.create_all()
            
            # Create test products
            product1 = Product(name="Apple Product", type=ProductType.STANDARD)
            product2 = Product(name="Apple Juice", type=ProductType.KIT)
            product3 = Product(name="Orange Product", type=ProductType.SEMI_PRODUCT)
            
            db.session.add_all([product1, product2, product3])
            db.session.commit()
            
            response = client.get('/api/v1/search/?q=apple')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'results' in data
            assert 'suggestions' in data
            assert 'query' in data
            assert 'total_results' in data
            assert 'search_time_ms' in data
            
            assert data['query'] == 'apple'
            assert data['total_results'] >= 2
    
    def test_advanced_search_with_filters(self, client, app):
        """Test advanced search with filters."""
        with app.app_context():
            db.create_all()
            
            # Create test products with different types
            product1 = Product(name="Test Product", type=ProductType.STANDARD)
            product2 = Product(name="Test Kit", type=ProductType.KIT)
            
            db.session.add_all([product1, product2])
            db.session.commit()
            
            # Search with type filter
            response = client.get('/api/v1/search/?q=test&type=kit')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['total_results'] >= 1
            # All results should be of type 'kit'
            for result in data['results']:
                assert result['type'] == 'kit'
    
    def test_advanced_search_empty_query(self, client, app):
        """Test advanced search with empty query."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/search/?q=')
            
            assert response.status_code == 400
    
    def test_advanced_search_invalid_filters(self, client, app):
        """Test advanced search with invalid filters."""
        with app.app_context():
            db.create_all()
            
            # Invalid type
            response = client.get('/api/v1/search/?q=test&type=invalid')
            assert response.status_code == 400
            
            # Invalid unit
            response = client.get('/api/v1/search/?q=test&unit=invalid')
            assert response.status_code == 400
            
            # Invalid similarity threshold
            response = client.get('/api/v1/search/?q=test&similarity_threshold=2.0')
            assert response.status_code == 400
    
    def test_advanced_search_with_limit(self, client, app):
        """Test advanced search with result limit."""
        with app.app_context():
            db.create_all()
            
            # Create multiple test products
            for i in range(10):
                product = Product(name=f"Product {i}")
                db.session.add(product)
            db.session.commit()
            
            response = client.get('/api/v1/search/?q=product&limit=3')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert len(data['results']) <= 3


class TestSearchSuggestionsAPI:
    """Test cases for Search Suggestions API endpoints."""
    
    def test_search_suggestions_basic(self, client, app):
        """Test basic search suggestions functionality."""
        with app.app_context():
            db.create_all()
            
            # Create test products
            product1 = Product(name="Apple Product")
            product2 = Product(name="Apple Juice")
            product3 = Product(name="Application")
            
            db.session.add_all([product1, product2, product3])
            db.session.commit()
            
            response = client.get('/api/v1/search/suggestions?q=app')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'suggestions' in data
            assert 'query' in data
            assert 'total_suggestions' in data
            
            assert data['query'] == 'app'
            assert isinstance(data['suggestions'], list)
    
    def test_search_suggestions_short_query(self, client, app):
        """Test search suggestions with short query."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/search/suggestions?q=a')
            
            assert response.status_code == 400
    
    def test_search_suggestions_empty_query(self, client, app):
        """Test search suggestions with empty query."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/search/suggestions?q=')
            
            assert response.status_code == 400
    
    def test_search_suggestions_with_limit(self, client, app):
        """Test search suggestions with limit."""
        with app.app_context():
            db.create_all()
            
            # Create many products starting with 'test'
            for i in range(20):
                product = Product(name=f"Test Product {i}")
                db.session.add(product)
            db.session.commit()
            
            response = client.get('/api/v1/search/suggestions?q=test&limit=5')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert len(data['suggestions']) <= 5


class TestPopularSearchesAPI:
    """Test cases for Popular Searches API endpoints."""
    
    def test_popular_searches_basic(self, client, app):
        """Test basic popular searches functionality."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/search/popular')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'popular_searches' in data
            assert 'total_count' in data
            
            assert isinstance(data['popular_searches'], list)
            assert isinstance(data['total_count'], int)


class TestSearchCacheAPI:
    """Test cases for Search Cache API endpoints."""
    
    def test_cache_cleanup(self, client, app):
        """Test search cache cleanup."""
        with app.app_context():
            db.create_all()
            
            response = client.delete('/api/v1/search/cache/cleanup')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'cleaned_entries' in data
            assert isinstance(data['cleaned_entries'], int)