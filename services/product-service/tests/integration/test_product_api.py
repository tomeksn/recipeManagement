"""Integration tests for Product API endpoints."""
import pytest
import json
import uuid
from flask import url_for

from app.models.product import Product, ProductCategory, ProductTag, ProductType, ProductUnit
from app.extensions import db


class TestProductAPI:
    """Test cases for Product API endpoints."""
    
    def test_get_products_empty(self, client, app):
        """Test getting products when none exist."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/products/')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['products'] == []
            assert data['pagination']['total'] == 0
    
    def test_create_product_success(self, client, app):
        """Test creating a product successfully."""
        with app.app_context():
            db.create_all()
            
            product_data = {
                'name': 'Test Product',
                'type': 'standard',
                'unit': 'piece',
                'description': 'A test product'
            }
            
            response = client.post(
                '/api/v1/products/',
                data=json.dumps(product_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['name'] == 'Test Product'
            assert data['type'] == 'standard'
            assert data['unit'] == 'piece'
            assert data['description'] == 'A test product'
            assert 'id' in data
    
    def test_create_product_duplicate_name(self, client, app):
        """Test creating product with duplicate name fails."""
        with app.app_context():
            db.create_all()
            
            # Create first product
            product1 = Product(name="Duplicate Name")
            db.session.add(product1)
            db.session.commit()
            
            # Try to create second product with same name
            product_data = {
                'name': 'Duplicate Name',
                'type': 'standard',
                'unit': 'piece'
            }
            
            response = client.post(
                '/api/v1/products/',
                data=json.dumps(product_data),
                content_type='application/json'
            )
            
            assert response.status_code == 409
            data = json.loads(response.data)
            assert 'already exists' in data['message']
    
    def test_create_product_invalid_data(self, client, app):
        """Test creating product with invalid data fails."""
        with app.app_context():
            db.create_all()
            
            product_data = {
                'name': '',  # Empty name
                'type': 'invalid_type',
                'unit': 'invalid_unit'
            }
            
            response = client.post(
                '/api/v1/products/',
                data=json.dumps(product_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
    
    def test_get_product_by_id_success(self, client, app):
        """Test getting product by ID successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test product
            product = Product(
                name="Test Product",
                type=ProductType.KIT,
                unit=ProductUnit.GRAM,
                description="Test description"
            )
            db.session.add(product)
            db.session.commit()
            
            response = client.get(f'/api/v1/products/{product.id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Test Product'
            assert data['type'] == 'kit'
            assert data['unit'] == 'gram'
            assert data['description'] == 'Test description'
    
    def test_get_product_by_id_not_found(self, client, app):
        """Test getting nonexistent product returns 404."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            response = client.get(f'/api/v1/products/{fake_id}')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'not found' in data['message']
    
    def test_update_product_success(self, client, app):
        """Test updating product successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test product
            product = Product(name="Original Name")
            db.session.add(product)
            db.session.commit()
            
            # Update product
            update_data = {
                'name': 'Updated Name',
                'description': 'Updated description'
            }
            
            response = client.put(
                f'/api/v1/products/{product.id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Updated Name'
            assert data['description'] == 'Updated description'
    
    def test_update_product_not_found(self, client, app):
        """Test updating nonexistent product returns 404."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            update_data = {'name': 'Updated Name'}
            
            response = client.put(
                f'/api/v1/products/{fake_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 404
    
    def test_update_product_duplicate_name(self, client, app):
        """Test updating product to duplicate name fails."""
        with app.app_context():
            db.create_all()
            
            # Create two products
            product1 = Product(name="Product 1")
            product2 = Product(name="Product 2")
            db.session.add_all([product1, product2])
            db.session.commit()
            
            # Try to update product2 to have same name as product1
            update_data = {'name': 'Product 1'}
            
            response = client.put(
                f'/api/v1/products/{product2.id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 409
    
    def test_delete_product_success(self, client, app):
        """Test deleting product successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test product
            product = Product(name="To Delete")
            db.session.add(product)
            db.session.commit()
            product_id = product.id
            
            response = client.delete(f'/api/v1/products/{product_id}')
            
            assert response.status_code == 204
            
            # Verify product is deleted
            get_response = client.get(f'/api/v1/products/{product_id}')
            assert get_response.status_code == 404
    
    def test_delete_product_not_found(self, client, app):
        """Test deleting nonexistent product returns 404."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            response = client.delete(f'/api/v1/products/{fake_id}')
            
            assert response.status_code == 404
    
    def test_get_products_with_pagination(self, client, app):
        """Test getting products with pagination."""
        with app.app_context():
            db.create_all()
            
            # Create test products
            products = []
            for i in range(5):
                product = Product(name=f"Product {i}")
                products.append(product)
                db.session.add(product)
            db.session.commit()
            
            # Test first page
            response = client.get('/api/v1/products/?page=1&per_page=3')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['products']) == 3
            assert data['pagination']['total'] == 5
            assert data['pagination']['pages'] == 2
            assert data['pagination']['has_next'] is True
            assert data['pagination']['has_prev'] is False
    
    def test_get_products_with_filters(self, client, app):
        """Test getting products with filters."""
        with app.app_context():
            db.create_all()
            
            # Create test products with different types
            product1 = Product(name="Standard Product", type=ProductType.STANDARD)
            product2 = Product(name="Kit Product", type=ProductType.KIT)
            product3 = Product(name="Semi Product", type=ProductType.SEMI_PRODUCT)
            
            db.session.add_all([product1, product2, product3])
            db.session.commit()
            
            # Test type filter
            response = client.get('/api/v1/products/?type=kit')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['products']) == 1
            assert data['products'][0]['name'] == 'Kit Product'
    
    def test_search_products_success(self, client, app):
        """Test searching products successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test products
            product1 = Product(name="Apple Product")
            product2 = Product(name="Banana Product")
            product3 = Product(name="Orange Juice")
            
            db.session.add_all([product1, product2, product3])
            db.session.commit()
            
            response = client.get('/api/v1/products/search?q=product')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['query'] == 'product'
            assert len(data['results']) >= 2  # Should find at least Apple Product and Banana Product
    
    def test_search_products_no_results(self, client, app):
        """Test searching products with no results."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/products/search?q=nonexistent')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['query'] == 'nonexistent'
            assert len(data['results']) == 0
    
    def test_search_products_invalid_query(self, client, app):
        """Test searching products with invalid query parameters."""
        with app.app_context():
            db.create_all()
            
            # Test empty query
            response = client.get('/api/v1/products/search?q=')
            assert response.status_code == 400
            
            # Test invalid limit
            response = client.get('/api/v1/products/search?q=test&limit=0')
            assert response.status_code == 400
            
            # Test invalid similarity threshold
            response = client.get('/api/v1/products/search?q=test&similarity_threshold=2.0')
            assert response.status_code == 400


class TestCategoryAPI:
    """Test cases for Category API endpoints."""
    
    def test_get_categories_empty(self, client, app):
        """Test getting categories when none exist."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/products/categories')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []
    
    def test_get_categories_with_data(self, client, app):
        """Test getting categories with existing data."""
        with app.app_context():
            db.create_all()
            
            # Create test categories
            category1 = ProductCategory(name="Category 1", color="#FF0000")
            category2 = ProductCategory(name="Category 2", color="#00FF00")
            
            db.session.add_all([category1, category2])
            db.session.commit()
            
            response = client.get('/api/v1/products/categories')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 2
            
            names = [cat['name'] for cat in data]
            assert 'Category 1' in names
            assert 'Category 2' in names


class TestTagAPI:
    """Test cases for Tag API endpoints."""
    
    def test_get_tags_empty(self, client, app):
        """Test getting tags when none exist."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/products/tags')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []
    
    def test_get_tags_with_data(self, client, app):
        """Test getting tags with existing data."""
        with app.app_context():
            db.create_all()
            
            # Create test tags
            tag1 = ProductTag(name="tag1")
            tag2 = ProductTag(name="tag2")
            
            db.session.add_all([tag1, tag2])
            db.session.commit()
            
            response = client.get('/api/v1/products/tags')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 2
            
            names = [tag['name'] for tag in data]
            assert 'tag1' in names
            assert 'tag2' in names