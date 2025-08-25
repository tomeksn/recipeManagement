"""Unit tests for Product Repository."""
import pytest
import uuid
from unittest.mock import Mock, patch

from app.models.product import Product, ProductType, ProductUnit
from app.services.product_repository import ProductRepository
from app.utils.exceptions import ProductNotFoundError, ProductAlreadyExistsError
from app.extensions import db


class TestProductRepository:
    """Test cases for ProductRepository."""
    
    def setup_method(self):
        """Setup test environment."""
        self.repository = ProductRepository()
    
    def test_get_by_id_existing(self, app):
        """Test getting existing product by ID."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test product
                product = Product(name="Test Product")
                db.session.add(product)
                db.session.commit()
                
                # Test retrieval
                result = self.repository.get_by_id(product.id)
                
                assert result is not None
                assert result.id == product.id
                assert result.name == "Test Product"
                
            finally:
                db.session.rollback()
    
    def test_get_by_id_nonexistent(self, app):
        """Test getting nonexistent product by ID."""
        with app.app_context():
            db.create_all()
            
            result = self.repository.get_by_id(uuid.uuid4())
            assert result is None
    
    def test_get_by_name_existing(self, app):
        """Test getting existing product by name."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test product
                product = Product(name="Test Product")
                db.session.add(product)
                db.session.commit()
                
                # Test retrieval (case insensitive)
                result = self.repository.get_by_name("test product")
                
                assert result is not None
                assert result.name == "Test Product"
                
            finally:
                db.session.rollback()
    
    def test_get_by_name_nonexistent(self, app):
        """Test getting nonexistent product by name."""
        with app.app_context():
            db.create_all()
            
            result = self.repository.get_by_name("Nonexistent Product")
            assert result is None
    
    def test_create_product_success(self, app):
        """Test creating product successfully."""
        with app.app_context():
            db.create_all()
            
            try:
                product_data = {
                    'name': 'New Product',
                    'type': 'kit',
                    'unit': 'gram',
                    'description': 'A new product'
                }
                
                created_by = uuid.uuid4()
                result = self.repository.create(product_data, created_by)
                
                assert result.name == 'New Product'
                assert result.type == ProductType.KIT
                assert result.unit == ProductUnit.GRAM
                assert result.description == 'A new product'
                assert result.created_by == created_by
                assert result.updated_by == created_by
                
            finally:
                db.session.rollback()
    
    def test_create_product_duplicate_name(self, app):
        """Test creating product with duplicate name."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create first product
                product1 = Product(name="Duplicate Name")
                db.session.add(product1)
                db.session.commit()
                
                # Try to create second product with same name
                product_data = {'name': 'Duplicate Name'}
                
                with pytest.raises(ProductAlreadyExistsError):
                    self.repository.create(product_data)
                
            finally:
                db.session.rollback()
    
    def test_update_product_success(self, app):
        """Test updating product successfully."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test product
                product = Product(name="Original Name")
                db.session.add(product)
                db.session.commit()
                
                # Update product
                update_data = {
                    'name': 'Updated Name',
                    'description': 'Updated description'
                }
                updated_by = uuid.uuid4()
                
                result = self.repository.update(product.id, update_data, updated_by)
                
                assert result.name == 'Updated Name'
                assert result.description == 'Updated description'
                assert result.updated_by == updated_by
                
            finally:
                db.session.rollback()
    
    def test_update_nonexistent_product(self, app):
        """Test updating nonexistent product."""
        with app.app_context():
            db.create_all()
            
            update_data = {'name': 'Updated Name'}
            
            with pytest.raises(ProductNotFoundError):
                self.repository.update(uuid.uuid4(), update_data)
    
    def test_delete_product_success(self, app):
        """Test deleting product successfully."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test product
                product = Product(name="To Delete")
                db.session.add(product)
                db.session.commit()
                product_id = product.id
                
                # Delete product
                result = self.repository.delete(product_id)
                
                assert result is True
                
                # Verify deletion
                deleted_product = self.repository.get_by_id(product_id)
                assert deleted_product is None
                
            finally:
                db.session.rollback()
    
    def test_delete_nonexistent_product(self, app):
        """Test deleting nonexistent product."""
        with app.app_context():
            db.create_all()
            
            result = self.repository.delete(uuid.uuid4())
            assert result is False
    
    def test_get_all_with_pagination(self, app):
        """Test getting all products with pagination."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test products
                products = []
                for i in range(5):
                    product = Product(name=f"Product {i}")
                    products.append(product)
                    db.session.add(product)
                db.session.commit()
                
                # Test pagination
                result_products, metadata = self.repository.get_all(page=1, per_page=3)
                
                assert len(result_products) == 3
                assert metadata['total'] == 5
                assert metadata['pages'] == 2
                assert metadata['has_next'] is True
                assert metadata['has_prev'] is False
                
            finally:
                db.session.rollback()
    
    def test_get_all_with_filters(self, app):
        """Test getting all products with filters."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test products with different types
                product1 = Product(name="Standard Product", type=ProductType.STANDARD)
                product2 = Product(name="Kit Product", type=ProductType.KIT)
                product3 = Product(name="Semi Product", type=ProductType.SEMI_PRODUCT)
                
                db.session.add_all([product1, product2, product3])
                db.session.commit()
                
                # Test type filter
                result_products, metadata = self.repository.get_all(
                    product_type=ProductType.KIT
                )
                
                assert len(result_products) == 1
                assert result_products[0].name == "Kit Product"
                
            finally:
                db.session.rollback()
    
    @patch('app.services.product_repository.ProductRepository._get_cached_search_result')
    @patch('app.services.product_repository.ProductRepository._cache_search_result')
    def test_search_fuzzy_with_cache(self, mock_cache, mock_get_cache, app):
        """Test fuzzy search with caching."""
        with app.app_context():
            db.create_all()
            
            # Mock cached result
            cached_results = [
                {
                    'id': str(uuid.uuid4()),
                    'name': 'Cached Product',
                    'type': 'standard',
                    'unit': 'piece',
                    'description': None,
                    'similarity_score': 0.8
                }
            ]
            mock_get_cache.return_value = cached_results
            
            # Test search
            results = self.repository.search_fuzzy('test', use_cache=True)
            
            assert results == cached_results
            mock_get_cache.assert_called_once()
            mock_cache.assert_not_called()  # Should not cache when result comes from cache
    
    def test_basic_search_fallback(self, app):
        """Test basic search fallback."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test products
                product1 = Product(name="Apple Product")
                product2 = Product(name="Banana Product")
                product3 = Product(name="Orange Juice")
                
                db.session.add_all([product1, product2, product3])
                db.session.commit()
                
                # Test basic search
                results = self.repository._basic_search('product', 10)
                
                assert len(results) == 2
                names = [r['name'] for r in results]
                assert 'Apple Product' in names
                assert 'Banana Product' in names
                assert 'Orange Juice' not in names
                
            finally:
                db.session.rollback()
    
    def test_generate_search_hash(self, app):
        """Test search hash generation."""
        with app.app_context():
            hash1 = self.repository._generate_search_hash('test', 10, 0.3)
            hash2 = self.repository._generate_search_hash('test', 10, 0.3)
            hash3 = self.repository._generate_search_hash('TEST', 10, 0.3)
            hash4 = self.repository._generate_search_hash('test', 20, 0.3)
            
            # Same parameters should generate same hash
            assert hash1 == hash2
            
            # Case insensitive
            assert hash1 == hash3
            
            # Different parameters should generate different hash
            assert hash1 != hash4
    
    def test_get_audit_history(self, app):
        """Test getting audit history for a product."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create test product
                product = Product(name="Test Product")
                db.session.add(product)
                db.session.commit()
                
                # Test audit history retrieval (should be empty initially)
                history = self.repository.get_audit_history(product.id)
                
                # Should return empty list for this test since we don't have audit triggers in test DB
                assert isinstance(history, list)
                
            finally:
                db.session.rollback()