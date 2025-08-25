"""Recipe model and related entities."""
import uuid
import enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey, Integer, Numeric, Boolean, Table, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from decimal import Decimal

from ..extensions import db


class RecipeStatus(enum.Enum):
    """Recipe status enumeration."""
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    DEPRECATED = 'deprecated'


class IngredientUnit(enum.Enum):
    """Ingredient unit enumeration."""
    PIECE = 'piece'
    GRAM = 'gram'
    MILLILITER = 'milliliter'
    LITER = 'liter'
    KILOGRAM = 'kilogram'


# Association table for recipe-tag many-to-many relationship
recipe_tag_assignments = Table(
    'recipe_tag_assignments',
    db.Model.metadata,
    Column('recipe_id', UUID(as_uuid=True), ForeignKey('recipe_service.recipes.id', ondelete='CASCADE'),
           primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('recipe_service.recipe_tags.id', ondelete='CASCADE'),
           primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=func.now()),
    schema='recipe_service'
)


class Recipe(db.Model):
    """Recipe model representing a product recipe."""
    
    __tablename__ = 'recipes'
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='recipes_name_not_empty'),
        CheckConstraint("version > 0", name='recipes_version_positive'),
        CheckConstraint("yield_quantity IS NULL OR yield_quantity > 0", 
                       name='recipes_yield_quantity_positive'),
        CheckConstraint("preparation_time IS NULL OR preparation_time > 0", 
                       name='recipes_preparation_time_positive'),
        {'schema': 'recipe_service'}
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Product relationship
    product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Recipe information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    version = Column(Integer, nullable=False, default=1, index=True)
    status = Column(Enum(RecipeStatus), nullable=False, default=RecipeStatus.DRAFT, index=True)
    
    # Recipe metadata
    yield_quantity = Column(Numeric(10, 3))
    yield_unit = Column(Enum(IngredientUnit))
    preparation_time = Column(Integer)  # in minutes
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(),
                       nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    ingredients = relationship('RecipeIngredient', back_populates='recipe', lazy='select',
                             cascade='all, delete-orphan',
                             order_by='RecipeIngredient.sort_order')
    
    versions = relationship('RecipeVersion', back_populates='recipe', lazy='dynamic')
    
    dependencies = relationship('RecipeDependency', back_populates='parent_recipe',
                              foreign_keys='RecipeDependency.parent_recipe_id')
    
    nutrition = relationship('RecipeNutrition', back_populates='recipe', uselist=False)
    
    tags = relationship('RecipeTag', secondary=recipe_tag_assignments, back_populates='recipes')
    
    audit_entries = relationship('RecipeAudit', lazy='dynamic',
                               primaryjoin='Recipe.id == RecipeAudit.recipe_id')
    
    # Unique constraint for product-version combination
    __table_args__ = (
        *__table_args__[:-1],  # Unpack existing constraints
        db.UniqueConstraint('product_id', 'version', name='recipes_product_version_unique'),
        {'schema': 'recipe_service'}
    )
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate recipe name."""
        if not name or not name.strip():
            raise ValueError("Recipe name cannot be empty")
        return name.strip()
    
    @validates('version')
    def validate_version(self, key, version):
        """Validate recipe version."""
        if version is not None and version <= 0:
            raise ValueError("Recipe version must be positive")
        return version
    
    @validates('yield_quantity')
    def validate_yield_quantity(self, key, quantity):
        """Validate yield quantity."""
        if quantity is not None and quantity <= 0:
            raise ValueError("Yield quantity must be positive")
        return quantity
    
    @validates('preparation_time')
    def validate_preparation_time(self, key, time):
        """Validate preparation time."""
        if time is not None and time <= 0:
            raise ValueError("Preparation time must be positive")
        return time
    
    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """Convert recipe to dictionary representation.
        
        Args:
            include_relationships: Whether to include ingredients and other relationships
            
        Returns:
            Dictionary representation of the recipe
        """
        result = {
            'id': str(self.id),
            'product_id': str(self.product_id),
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'status': self.status.value,
            'yield_quantity': float(self.yield_quantity) if self.yield_quantity else None,
            'yield_unit': self.yield_unit.value if self.yield_unit else None,
            'preparation_time': self.preparation_time,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
        
        if include_relationships:
            result['ingredients'] = [ingredient.to_dict() for ingredient in self.ingredients]
            result['tags'] = [tag.to_dict() for tag in self.tags]
            if self.nutrition:
                result['nutrition'] = self.nutrition.to_dict()
        
        return result
    
    def get_total_ingredients_count(self) -> int:
        """Get total number of ingredients in this recipe."""
        return len(self.ingredients)
    
    def get_required_ingredients_count(self) -> int:
        """Get number of required (non-optional) ingredients."""
        return len([ing for ing in self.ingredients if not ing.is_optional])
    
    def __repr__(self):
        return f'<Recipe {self.name} v{self.version} ({self.status.value})>'


class RecipeIngredient(db.Model):
    """Recipe ingredient model representing an ingredient in a recipe."""
    
    __tablename__ = 'recipe_ingredients'
    __table_args__ = (
        CheckConstraint("quantity > 0", name='recipe_ingredients_quantity_positive'),
        CheckConstraint("sort_order >= 0", name='recipe_ingredients_sort_order_non_negative'),
        db.UniqueConstraint('recipe_id', 'ingredient_product_id', 
                          name='recipe_ingredients_unique_ingredient'),
        {'schema': 'recipe_service'}
    )
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Recipe relationship
    recipe_id = Column(UUID(as_uuid=True), ForeignKey('recipe_service.recipes.id', ondelete='CASCADE'),
                      nullable=False, index=True)
    
    # Ingredient information
    ingredient_product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(Enum(IngredientUnit), nullable=False)
    
    # Ordering and organization
    sort_order = Column(Integer, nullable=False, default=0, index=True)
    ingredient_group = Column(String(100), index=True)
    
    # Additional metadata
    notes = Column(Text)
    is_optional = Column(Boolean, nullable=False, default=False)
    substitute_ingredients = Column(JSONB)  # Array of alternative ingredient IDs
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(),
                       nullable=False)
    
    # Relationships
    recipe = relationship('Recipe', back_populates='ingredients')
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        """Validate ingredient quantity."""
        if quantity is not None and quantity <= 0:
            raise ValueError("Ingredient quantity must be positive")
        return quantity
    
    @validates('sort_order')
    def validate_sort_order(self, key, sort_order):
        """Validate sort order."""
        if sort_order is not None and sort_order < 0:
            raise ValueError("Sort order must be non-negative")
        return sort_order
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ingredient to dictionary representation."""
        return {
            'id': str(self.id),
            'recipe_id': str(self.recipe_id),
            'ingredient_product_id': str(self.ingredient_product_id),
            'quantity': float(self.quantity),
            'unit': self.unit.value,
            'sort_order': self.sort_order,
            'ingredient_group': self.ingredient_group,
            'notes': self.notes,
            'is_optional': self.is_optional,
            'substitute_ingredients': self.substitute_ingredients,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<RecipeIngredient {self.ingredient_product_id} ({self.quantity} {self.unit.value})>'


class RecipeVersion(db.Model):
    """Recipe version model for tracking version history."""
    
    __tablename__ = 'recipe_versions'
    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'version_number', 
                          name='recipe_versions_unique_version'),
        {'schema': 'recipe_service'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey('recipe_service.recipes.id', ondelete='CASCADE'),
                      nullable=False, index=True)
    version_number = Column(Integer, nullable=False, index=True)
    recipe_data = Column(JSONB, nullable=False)  # Complete recipe snapshot
    change_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    recipe = relationship('Recipe', back_populates='versions')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary representation."""
        return {
            'id': str(self.id),
            'recipe_id': str(self.recipe_id),
            'version_number': self.version_number,
            'recipe_data': self.recipe_data,
            'change_summary': self.change_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': str(self.created_by) if self.created_by else None
        }
    
    def __repr__(self):
        return f'<RecipeVersion {self.recipe_id} v{self.version_number}>'


class RecipeDependency(db.Model):
    """Recipe dependency model for tracking hierarchical relationships."""
    
    __tablename__ = 'recipe_dependencies'
    __table_args__ = (
        CheckConstraint("parent_recipe_id != child_product_id::UUID", 
                       name='recipe_dependencies_no_self_reference'),
        db.UniqueConstraint('parent_recipe_id', 'child_product_id',
                          name='recipe_dependencies_unique_dependency'),
        {'schema': 'recipe_service'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_recipe_id = Column(UUID(as_uuid=True), 
                             ForeignKey('recipe_service.recipes.id', ondelete='CASCADE'),
                             nullable=False, index=True)
    child_product_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    dependency_type = Column(String(50), nullable=False, default='ingredient')
    depth_level = Column(Integer, nullable=False, default=1, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    parent_recipe = relationship('Recipe', back_populates='dependencies')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dependency to dictionary representation."""
        return {
            'id': str(self.id),
            'parent_recipe_id': str(self.parent_recipe_id),
            'child_product_id': str(self.child_product_id),
            'dependency_type': self.dependency_type,
            'depth_level': self.depth_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<RecipeDependency {self.parent_recipe_id} -> {self.child_product_id}>'


class RecipeNutrition(db.Model):
    """Recipe nutrition model for nutritional information."""
    
    __tablename__ = 'recipe_nutrition'
    __table_args__ = (
        CheckConstraint("""
            (calories IS NULL OR calories >= 0) AND
            (protein IS NULL OR protein >= 0) AND
            (carbohydrates IS NULL OR carbohydrates >= 0) AND
            (fat IS NULL OR fat >= 0) AND
            (fiber IS NULL OR fiber >= 0) AND
            (sugar IS NULL OR sugar >= 0) AND
            (sodium IS NULL OR sodium >= 0)
        """, name='recipe_nutrition_values_non_negative'),
        {'schema': 'recipe_service'}
    )
    
    recipe_id = Column(UUID(as_uuid=True), 
                      ForeignKey('recipe_service.recipes.id', ondelete='CASCADE'),
                      primary_key=True)
    
    # Macronutrients per 100g/100ml
    calories = Column(Numeric(8, 2))
    protein = Column(Numeric(8, 2))
    carbohydrates = Column(Numeric(8, 2))
    fat = Column(Numeric(8, 2))
    fiber = Column(Numeric(8, 2))
    sugar = Column(Numeric(8, 2))
    sodium = Column(Numeric(8, 2))
    
    # Calculation metadata
    calculated_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    calculation_method = Column(String(100))  # 'manual', 'automated', 'imported'
    
    # Relationships
    recipe = relationship('Recipe', back_populates='nutrition')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert nutrition to dictionary representation."""
        return {
            'recipe_id': str(self.recipe_id),
            'calories': float(self.calories) if self.calories else None,
            'protein': float(self.protein) if self.protein else None,
            'carbohydrates': float(self.carbohydrates) if self.carbohydrates else None,
            'fat': float(self.fat) if self.fat else None,
            'fiber': float(self.fiber) if self.fiber else None,
            'sugar': float(self.sugar) if self.sugar else None,
            'sodium': float(self.sodium) if self.sodium else None,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'calculation_method': self.calculation_method
        }
    
    def __repr__(self):
        return f'<RecipeNutrition {self.recipe_id}>'


class RecipeTag(db.Model):
    """Recipe tag model for flexible tagging."""
    
    __tablename__ = 'recipe_tags'
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name='recipe_tags_name_not_empty'),
        CheckConstraint("color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'", 
                       name='recipe_tags_color_format'),
        {'schema': 'recipe_service'}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7))  # Hex color code
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    recipes = relationship('Recipe', secondary=recipe_tag_assignments, back_populates='tags')
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate tag name."""
        if not name or not name.strip():
            raise ValueError("Tag name cannot be empty")
        return name.strip()
    
    @validates('color')
    def validate_color(self, key, color):
        """Validate color format."""
        if color is not None:
            import re
            if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                raise ValueError("Color must be a valid hex color code (e.g., #FF0000)")
        return color
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tag to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<RecipeTag {self.name}>'


class RecipeAudit(db.Model):
    """Recipe audit model for comprehensive change tracking."""
    
    __tablename__ = 'recipe_audit'
    __table_args__ = (
        CheckConstraint("operation IN ('INSERT', 'UPDATE', 'DELETE', 'VERSION_CREATE')",
                       name='recipe_audit_operation_check'),
        {'schema': 'recipe_service'}
    )
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey('recipe_service.recipes.id'), nullable=False, index=True)
    ingredient_id = Column(UUID(as_uuid=True))  # NULL for recipe-level changes
    operation = Column(String(20), nullable=False, index=True)
    table_name = Column(String(50), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True))
    changed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary representation."""
        return {
            'audit_id': str(self.audit_id),
            'recipe_id': str(self.recipe_id),
            'ingredient_id': str(self.ingredient_id) if self.ingredient_id else None,
            'operation': self.operation,
            'table_name': self.table_name,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'changed_by': str(self.changed_by) if self.changed_by else None,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }
    
    def __repr__(self):
        return f'<RecipeAudit {self.operation} on {self.recipe_id}>'