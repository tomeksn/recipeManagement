"""Product model and related entities."""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey, Table, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import enum

from ..extensions import db


class ProductType(enum.Enum):
    """Product type enumeration."""
    STANDARD = 'standard'
    KIT = 'kit'
    SEMI_PRODUCT = 'semi-product'


class ProductUnit(enum.Enum):
    """Product unit enumeration."""
    PIECE = 'piece'
    GRAM = 'gram'


# Association table for product-category many-to-many relationship
product_category_assignments = Table(
    'product_category_assignments',
    db.Model.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('product_service.products.id', ondelete='CASCADE'),
           primary_key=True),
    Column('category_id', UUID(as_uuid=True), ForeignKey('product_service.product_categories.id', ondelete='CASCADE'),
           primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=func.now()),
    schema='product_service'
)

# Association table for product-tag many-to-many relationship
product_tag_assignments = Table(
    'product_tag_assignments',
    db.Model.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('product_service.products.id', ondelete='CASCADE'),
           primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('product_service.product_tags.id', ondelete='CASCADE'),
           primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=func.now()),
    schema='product_service'
)


class Product(db.Model):
    """Product model representing a product entity."""
    
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='products_name_not_empty'),
        {'schema': 'product_service'}
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic product information
    name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False, default='standard', index=True)
    unit = Column(String(50), nullable=False, default='piece', index=True)
    description = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(),
                       nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True))  # Reference to user
    updated_by = Column(UUID(as_uuid=True))  # Reference to user
    
    # Relationships
    categories = relationship(
        'ProductCategory',
        secondary=product_category_assignments,
        back_populates='products',
        lazy='select'
    )
    
    tags = relationship(
        'ProductTag',
        secondary=product_tag_assignments,
        back_populates='products',
        lazy='select'
    )
    
    audit_entries = relationship('ProductAudit', back_populates='product', lazy='dynamic')
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate product name."""
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")
        return name.strip()
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Convert product to dictionary representation.
        
        Args:
            include_relationships: Whether to include category and tag relationships
            
        Returns:
            Dictionary representation of the product
        """
        result = {
            'id': str(self.id),
            'name': self.name,
            'type': self.type,
            'unit': self.unit,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
        
        if include_relationships:
            result['categories'] = [cat.to_dict() for cat in self.categories]
            result['tags'] = [tag.to_dict() for tag in self.tags]
        
        return result
    
    def __repr__(self):
        return f'<Product {self.name} ({self.type})>'


class ProductCategory(db.Model):
    """Product category model for flexible categorization."""
    
    __tablename__ = 'product_categories'
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='product_categories_name_not_empty'),
        CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name='product_categories_color_format'),
        {'schema': 'product_service'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code for UI
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    products = relationship(
        'Product',
        secondary=product_category_assignments,
        back_populates='categories',
        lazy='select'
    )
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate category name."""
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty")
        return name.strip()
    
    @validates('color')
    def validate_color(self, key, color):
        """Validate color format."""
        if color is not None:
            import re
            if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return color
    
    def to_dict(self) -> dict:
        """Convert category to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ProductCategory {self.name}>'


class ProductTag(db.Model):
    """Product tag model for flexible tagging."""
    
    __tablename__ = 'product_tags'
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='product_tags_name_not_empty'),
        {'schema': 'product_service'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    products = relationship(
        'Product',
        secondary=product_tag_assignments,
        back_populates='tags',
        lazy='select'
    )
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate tag name."""
        if not name or not name.strip():
            raise ValueError("Tag name cannot be empty")
        return name.strip()
    
    def to_dict(self) -> dict:
        """Convert tag to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ProductTag {self.name}>'


class ProductAudit(db.Model):
    """Product audit model for tracking changes."""
    
    __tablename__ = 'products_audit'
    __table_args__ = (
        CheckConstraint("operation IN ('INSERT', 'UPDATE', 'DELETE')",
                       name='products_audit_operation_check'),
        {'schema': 'product_service'}
    )
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('product_service.products.id'),
                       nullable=False, index=True)
    operation = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True))
    changed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    # Relationships
    product = relationship('Product', back_populates='audit_entries')
    
    def to_dict(self) -> dict:
        """Convert audit entry to dictionary representation."""
        return {
            'audit_id': str(self.audit_id),
            'product_id': str(self.product_id),
            'operation': self.operation,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'changed_by': str(self.changed_by) if self.changed_by else None,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }
    
    def __repr__(self):
        return f'<ProductAudit {self.operation} on {self.product_id}>'


class ProductSearchCache(db.Model):
    """Search cache model for search optimization."""
    
    __tablename__ = 'product_search_cache'
    __table_args__ = {'schema': 'product_service'}
    
    search_hash = Column(String(64), primary_key=True)
    search_term = Column(String(255), nullable=False)
    results = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    def to_dict(self) -> dict:
        """Convert search cache entry to dictionary representation."""
        return {
            'search_hash': self.search_hash,
            'search_term': self.search_term,
            'results': self.results,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def __repr__(self):
        return f'<ProductSearchCache {self.search_term}>'