"""Unit tests for SearchService."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.services.search_service import ProductSearchService
from app.models.product import Product, ProductType, ProductUnit, ProductSearchCache
from app.extensions import db


class TestProductSearchService:
    """Test cases for ProductSearchService."""
    
    def setup_method(self):
        """Setup test environment."""
        self.search_service = ProductSearchService()
    
    def test_normalize_query(self, app):
        """Test query normalization."""
        with app.app_context():
            # Test basic normalization
            assert self.search_service._normalize_query("  Test Query  ") == "test query"
            
            # Test special character removal
            assert self.search_service._normalize_query("test@#$query!") == "testquery"
            
            # Test multiple spaces
            assert self.search_service._normalize_query("test    query") == "test query"
            
            # Test empty query
            assert self.search_service._normalize_query("") == ""
            assert self.search_service._normalize_query("   ") == ""
    
    def test_matches_filters_type(self, app):
        """Test product filtering by type."""
        with app.app_context():
            product = Product(name="Test", type=ProductType.KIT)
            
            # Matching filter
            assert self.search_service._matches_filters(product, {'type': 'kit'}) is True
            
            # Non-matching filter
            assert self.search_service._matches_filters(product, {'type': 'standard'}) is False
    
    def test_matches_filters_unit(self, app):
        """Test product filtering by unit."""
        with app.app_context():
            product = Product(name="Test", unit=ProductUnit.GRAM)
            
            # Matching filter
            assert self.search_service._matches_filters(product, {'unit': 'gram'}) is True
            
            # Non-matching filter
            assert self.search_service._matches_filters(product, {'unit': 'piece'}) is False
    
    def test_matches_filters_multiple(self, app):
        """Test product filtering with multiple filters."""
        with app.app_context():
            product = Product(name="Test", type=ProductType.KIT, unit=ProductUnit.GRAM)
            
            # All matching filters
            filters = {'type': 'kit', 'unit': 'gram'}
            assert self.search_service._matches_filters(product, filters) is True
            
            # One non-matching filter
            filters = {'type': 'kit', 'unit': 'piece'}
            assert self.search_service._matches_filters(product, filters) is False
    
    def test_generate_advanced_search_cache_key(self, app):
        """Test cache key generation."""
        with app.app_context():
            # Test with no filters
            key1 = self.search_service._generate_advanced_search_cache_key(
                "test", {}, 10, 0.3
            )
            
            # Test with filters
            key2 = self.search_service._generate_advanced_search_cache_key(
                "test", {'type': 'kit'}, 10, 0.3
            )
            
            # Keys should be different
            assert key1 != key2
            
            # Same parameters should generate same key
            key3 = self.search_service._generate_advanced_search_cache_key(
                "test", {}, 10, 0.3
            )
            assert key1 == key3
    
    def test_get_typo_corrections(self, app):
        """Test typo correction functionality."""
        with app.app_context():
            # Test known typo correction
            corrections = self.search_service._get_typo_corrections("recpie")
            assert "recipe" in corrections
            
            # Test unknown word
            corrections = self.search_service._get_typo_corrections("unknownword")
            assert corrections == []
    
    @patch('app.services.search_service.ProductSearchService._get_from_cache')
    @patch('app.services.search_service.ProductSearchService._cache_result')
    @patch('app.services.search_service.ProductSearchService._perform_filtered_search')
    def test_advanced_search_with_cache_hit(self, mock_search, mock_cache, mock_get_cache, app):
        """Test advanced search with cache hit."""
        with app.app_context():
            # Mock cached result
            cached_result = {
                'results': [{'id': 'test-id', 'name': 'Cached Product'}],
                'suggestions': [],
                'query': 'test',
                'total_results': 1
            }
            mock_get_cache.return_value = cached_result
            
            result = self.search_service.advanced_search('test')
            
            # Should return cached result
            assert result == cached_result
            
            # Should not perform actual search
            mock_search.assert_not_called()
            mock_cache.assert_not_called()
    
    @patch('app.services.search_service.ProductSearchService._get_from_cache')
    @patch('app.services.search_service.ProductSearchService._cache_result')
    @patch('app.services.search_service.ProductSearchService._perform_filtered_search')
    @patch('app.services.search_service.ProductSearchService._generate_search_suggestions')
    def test_advanced_search_cache_miss(self, mock_suggestions, mock_search, mock_cache, mock_get_cache, app):
        """Test advanced search with cache miss."""
        with app.app_context():
            # Mock cache miss
            mock_get_cache.return_value = None
            
            # Mock search results
            search_results = [{'id': 'test-id', 'name': 'Test Product'}]
            mock_search.return_value = search_results
            
            # Mock suggestions (for few results)
            suggestions = ['suggestion1', 'suggestion2']
            mock_suggestions.return_value = suggestions
            
            result = self.search_service.advanced_search('test')
            
            # Should perform search and cache result
            mock_search.assert_called_once()
            mock_cache.assert_called_once()
            
            # Should include suggestions for few results
            mock_suggestions.assert_called_once()
            
            assert result['results'] == search_results
            assert result['suggestions'] == suggestions
    
    def test_get_search_suggestions_short_query(self, app):
        """Test search suggestions with short query."""
        with app.app_context():
            suggestions = self.search_service.get_search_suggestions('a')
            assert suggestions == []
    
    def test_get_search_suggestions_empty_query(self, app):
        """Test search suggestions with empty query."""
        with app.app_context():
            suggestions = self.search_service.get_search_suggestions('')
            assert suggestions == []
    
    def test_cleanup_expired_cache(self, app):
        """Test cleaning up expired cache entries."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create expired cache entry
                expired_entry = ProductSearchCache(
                    search_hash="expired_hash",
                    search_term="expired search",
                    results={'test': 'data'},
                    expires_at=datetime.utcnow() - timedelta(hours=1)
                )
                
                # Create valid cache entry
                valid_entry = ProductSearchCache(
                    search_hash="valid_hash",
                    search_term="valid search",
                    results={'test': 'data'},
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                
                db.session.add_all([expired_entry, valid_entry])
                db.session.commit()
                
                # Clean up expired entries
                cleaned_count = self.search_service.cleanup_expired_cache()
                
                # Should clean up 1 expired entry
                assert cleaned_count == 1
                
                # Verify only valid entry remains
                remaining_entries = db.session.query(ProductSearchCache).all()
                assert len(remaining_entries) == 1
                assert remaining_entries[0].search_hash == "valid_hash"
                
            finally:
                db.session.rollback()
    
    @patch('app.services.search_service.db.session')
    def test_get_popular_searches_exception_handling(self, mock_session, app):
        """Test popular searches with exception handling."""
        with app.app_context():
            # Mock database exception
            mock_session.query.side_effect = Exception("Database error")
            
            result = self.search_service.get_popular_searches()
            
            # Should return empty list on exception
            assert result == []
    
    @patch('app.services.search_service.db.session')
    def test_cache_result_exception_handling(self, mock_session, app):
        """Test cache result with exception handling."""
        with app.app_context():
            # Mock database exception
            mock_session.add.side_effect = Exception("Database error")
            
            # Should not raise exception
            try:
                self.search_service._cache_result("test_key", {"test": "data"})
                # If we get here, exception was handled properly
                assert True
            except Exception:
                # Should not reach here
                assert False, "Exception should have been handled"