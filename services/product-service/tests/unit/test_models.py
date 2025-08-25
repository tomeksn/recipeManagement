"""Unit tests for Product models."""
import pytest
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.product import Product, ProductCategory, ProductTag, ProductType, ProductUnit
from app.extensions import db


class TestProductModel:
    """Test cases for Product model."""
    
    def test_create_product_with_required_fields(self, app):
        """Test creating product with required fields only."""
        with app.app_context():
            product = Product(name="Test Product")
            
            assert product.name == "Test Product"
            assert product.type == ProductType.STANDARD
            assert product.unit == ProductUnit.PIECE
            assert product.description is None
            assert product.id is not None
    
    def test_create_product_with_all_fields(self, app):
        """Test creating product with all fields."""
        with app.app_context():
            product_id = uuid.uuid4()
            user_id = uuid.uuid4()
            
            product = Product(
                id=product_id,
                name="Complete Product",
                type=ProductType.KIT,
                unit=ProductUnit.GRAM,
                description="A complete product description",
                created_by=user_id,
                updated_by=user_id
            )
            
            assert product.id == product_id
            assert product.name == "Complete Product"
            assert product.type == ProductType.KIT
            assert product.unit == ProductUnit.GRAM
            assert product.description == "A complete product description"
            assert product.created_by == user_id
            assert product.updated_by == user_id
    
    def test_product_name_validation(self, app):
        """Test product name validation."""
        with app.app_context():
            # Test empty name
            with pytest.raises(ValueError, match="Product name cannot be empty"):
                Product(name="")
            
            # Test whitespace-only name
            with pytest.raises(ValueError, match="Product name cannot be empty"):
                Product(name="   ")
            
            # Test name trimming
            product = Product(name="  Test Product  ")
            assert product.name == "Test Product"
    
    def test_product_to_dict(self, app):
        """Test product to_dict method."""
        with app.app_context():
            product = Product(
                name="Test Product",
                type=ProductType.SEMI_PRODUCT,
                unit=ProductUnit.GRAM,
                description="Test description"
            )
            
            result = product.to_dict()
            
            assert result['name'] == "Test Product"
            assert result['type'] == "semi-product"
            assert result['unit'] == "gram"
            assert result['description'] == "Test description"
            assert 'id' in result
            assert 'created_at' in result
            assert 'updated_at' in result
    
    def test_product_repr(self, app):
        """Test product string representation."""
        with app.app_context():
            product = Product(name="Test Product", type=ProductType.KIT)
            assert repr(product) == "<Product Test Product (kit)>"


class TestProductCategoryModel:
    """Test cases for ProductCategory model."""
    
    def test_create_category_with_required_fields(self, app):
        """Test creating category with required fields only."""
        with app.app_context():
            category = ProductCategory(name="Test Category")
            
            assert category.name == "Test Category"
            assert category.description is None
            assert category.color is None
            assert category.id is not None
    
    def test_create_category_with_all_fields(self, app):
        """Test creating category with all fields."""
        with app.app_context():
            category = ProductCategory(
                name="Complete Category",
                description="A complete category",
                color="#FF0000"
            )
            
            assert category.name == "Complete Category"
            assert category.description == "A complete category"
            assert category.color == "#FF0000"
    
    def test_category_name_validation(self, app):
        """Test category name validation."""
        with app.app_context():
            # Test empty name
            with pytest.raises(ValueError, match="Category name cannot be empty"):
                ProductCategory(name="")
            
            # Test name trimming
            category = ProductCategory(name="  Test Category  ")
            assert category.name == "Test Category"
    
    def test_category_color_validation(self, app):
        """Test category color validation."""
        with app.app_context():
            # Test valid color
            category = ProductCategory(name="Test", color="#FF0000")
            assert category.color == "#FF0000"
            
            # Test invalid color format
            with pytest.raises(ValueError, match="Color must be a valid hex color code"):
                ProductCategory(name="Test", color="red")
            
            with pytest.raises(ValueError, match="Color must be a valid hex color code"):
                ProductCategory(name="Test", color="#FF")
    
    def test_category_to_dict(self, app):
        """Test category to_dict method."""
        with app.app_context():
            category = ProductCategory(
                name="Test Category",
                description="Test description",
                color="#FF0000"
            )
            
            result = category.to_dict()
            
            assert result['name'] == "Test Category"
            assert result['description'] == "Test description"
            assert result['color'] == "#FF0000"
            assert 'id' in result
            assert 'created_at' in result


class TestProductTagModel:
    """Test cases for ProductTag model."""
    
    def test_create_tag(self, app):
        """Test creating tag."""
        with app.app_context():
            tag = ProductTag(name="test-tag")
            
            assert tag.name == "test-tag"
            assert tag.id is not None
    
    def test_tag_name_validation(self, app):
        """Test tag name validation."""
        with app.app_context():
            # Test empty name
            with pytest.raises(ValueError, match="Tag name cannot be empty"):
                ProductTag(name="")
            
            # Test name trimming
            tag = ProductTag(name="  test-tag  ")
            assert tag.name == "test-tag"
    
    def test_tag_to_dict(self, app):
        """Test tag to_dict method."""
        with app.app_context():
            tag = ProductTag(name="test-tag")
            
            result = tag.to_dict()
            
            assert result['name'] == "test-tag"
            assert 'id' in result
            assert 'created_at' in result


class TestProductRelationships:
    """Test product relationships."""
    
    def test_product_category_relationship(self, app):
        """Test product-category many-to-many relationship."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create product and category
                product = Product(name="Test Product")
                category = ProductCategory(name="Test Category")
                
                db.session.add(product)
                db.session.add(category)
                db.session.commit()
                
                # Associate them
                product.categories.append(category)
                db.session.commit()
                
                # Test relationship
                assert len(product.categories) == 1
                assert product.categories[0].name == "Test Category"
                assert len(category.products) == 1
                assert category.products[0].name == "Test Product"
                
            finally:
                db.session.rollback()
    
    def test_product_tag_relationship(self, app):
        """Test product-tag many-to-many relationship."""
        with app.app_context():
            db.create_all()
            
            try:
                # Create product and tag
                product = Product(name="Test Product")
                tag = ProductTag(name="test-tag")
                
                db.session.add(product)
                db.session.add(tag)
                db.session.commit()
                
                # Associate them
                product.tags.append(tag)
                db.session.commit()
                
                # Test relationship
                assert len(product.tags) == 1
                assert product.tags[0].name == "test-tag"
                assert len(tag.products) == 1
                assert tag.products[0].name == "Test Product"
                
            finally:
                db.session.rollback()