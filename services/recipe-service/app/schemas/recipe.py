"""Recipe API schemas for request/response validation."""
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from uuid import UUID
from decimal import Decimal

from ..models.recipe import Recipe, RecipeIngredient, RecipeTag, RecipeStatus, IngredientUnit


class RecipeStatusField(fields.Field):
    """Custom field for RecipeStatus enum."""
    
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value
    
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return RecipeStatus(value)
        except ValueError:
            raise ValidationError(f"Invalid recipe status: {value}")


class IngredientUnitField(fields.Field):
    """Custom field for IngredientUnit enum."""
    
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value
    
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return IngredientUnit(value)
        except ValueError:
            raise ValidationError(f"Invalid ingredient unit: {value}")


class RecipeIngredientSchema(Schema):
    """Schema for RecipeIngredient."""
    
    id = fields.UUID(dump_only=True)
    recipe_id = fields.UUID(dump_only=True)
    ingredient_product_id = fields.UUID(
        required=True,
        metadata={'description': 'Product UUID for the ingredient'}
    )
    quantity = fields.Decimal(
        required=True,
        validate=validate.Range(min=0.001),
        metadata={'description': 'Quantity of ingredient needed'}
    )
    unit = fields.Str(
        required=True,
        validate=validate.OneOf([u.value for u in IngredientUnit]),
        metadata={'description': 'Unit of measurement'}
    )
    sort_order = fields.Int(
        validate=validate.Range(min=0),
        missing=0,
        metadata={'description': 'Display order of ingredient'}
    )
    ingredient_group = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100),
        metadata={'description': 'Optional grouping (e.g., "Base", "Seasoning")'}
    )
    notes = fields.Str(
        allow_none=True,
        metadata={'description': 'Additional notes about the ingredient'}
    )
    is_optional = fields.Bool(
        missing=False,
        metadata={'description': 'Whether the ingredient is optional'}
    )
    substitute_ingredients = fields.List(
        fields.UUID(),
        allow_none=True,
        metadata={'description': 'Alternative ingredient product IDs'}
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('quantity')
    def validate_quantity(self, value):
        """Validate ingredient quantity."""
        if value is not None and value <= 0:
            raise ValidationError("Quantity must be positive")


class RecipeTagSchema(Schema):
    """Schema for RecipeTag."""
    
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    color = fields.Str(
        allow_none=True,
        validate=validate.Regexp(
            r'^#[0-9A-Fa-f]{6}$',
            error='Color must be a valid hex color code (e.g., #FF0000)'
        )
    )
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class RecipeNutritionSchema(Schema):
    """Schema for RecipeNutrition."""
    
    recipe_id = fields.UUID(dump_only=True)
    calories = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    protein = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    carbohydrates = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    fat = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    fiber = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    sugar = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    sodium = fields.Decimal(allow_none=True, validate=validate.Range(min=0))
    calculated_at = fields.DateTime(dump_only=True)
    calculation_method = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['manual', 'automated', 'imported'])
    )


class RecipeCreateSchema(Schema):
    """Schema for creating a recipe."""
    
    product_id = fields.UUID(
        required=True,
        metadata={'description': 'Product UUID this recipe produces'}
    )
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={'description': 'Recipe name'}
    )
    description = fields.Str(
        allow_none=True,
        metadata={'description': 'Recipe description'}
    )
    status = fields.Str(
        validate=validate.OneOf([s.value for s in RecipeStatus]),
        missing='draft',
        metadata={'description': 'Recipe status: draft, active, archived, deprecated'}
    )
    yield_quantity = fields.Decimal(
        allow_none=True,
        validate=validate.Range(min=0.001),
        metadata={'description': 'Expected yield quantity'}
    )
    yield_unit = fields.Str(
        allow_none=True,
        validate=validate.OneOf([u.value for u in IngredientUnit]),
        metadata={'description': 'Unit for yield quantity'}
    )
    preparation_time = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1),
        metadata={'description': 'Preparation time in minutes'}
    )
    notes = fields.Str(
        allow_none=True,
        metadata={'description': 'Additional recipe notes'}
    )
    ingredients = fields.List(
        fields.Nested(RecipeIngredientSchema),
        required=True,
        validate=validate.Length(min=1),
        metadata={'description': 'List of recipe ingredients'}
    )
    tag_ids = fields.List(
        fields.UUID(),
        missing=[],
        metadata={'description': 'List of tag UUIDs to assign'}
    )
    nutrition = fields.Nested(
        RecipeNutritionSchema,
        allow_none=True,
        metadata={'description': 'Nutritional information'}
    )
    
    @validates('name')
    def validate_name(self, value):
        """Validate recipe name."""
        if not value or not value.strip():
            raise ValidationError("Name cannot be empty")
    
    @validates('ingredients')
    def validate_ingredients(self, value):
        """Validate ingredients list."""
        if not value:
            raise ValidationError("Recipe must have at least one ingredient")
        
        # Check for duplicate ingredients
        ingredient_ids = [ing.get('ingredient_product_id') for ing in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError("Duplicate ingredients are not allowed")
    
    @post_load
    def trim_name(self, data, **kwargs):
        """Trim whitespace from name."""
        if 'name' in data:
            data['name'] = data['name'].strip()
        return data


class RecipeUpdateSchema(Schema):
    """Schema for updating a recipe."""
    
    name = fields.Str(
        validate=validate.Length(min=1, max=255),
        metadata={'description': 'Recipe name'}
    )
    description = fields.Str(
        allow_none=True,
        metadata={'description': 'Recipe description'}
    )
    status = fields.Str(
        validate=validate.OneOf([s.value for s in RecipeStatus]),
        metadata={'description': 'Recipe status'}
    )
    yield_quantity = fields.Decimal(
        allow_none=True,
        validate=validate.Range(min=0.001),
        metadata={'description': 'Expected yield quantity'}
    )
    yield_unit = fields.Str(
        allow_none=True,
        validate=validate.OneOf([u.value for u in IngredientUnit]),
        metadata={'description': 'Unit for yield quantity'}
    )
    preparation_time = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1),
        metadata={'description': 'Preparation time in minutes'}
    )
    notes = fields.Str(
        allow_none=True,
        metadata={'description': 'Additional recipe notes'}
    )
    ingredients = fields.List(
        fields.Nested(RecipeIngredientSchema),
        validate=validate.Length(min=1),
        metadata={'description': 'List of recipe ingredients'}
    )
    tag_ids = fields.List(
        fields.UUID(),
        metadata={'description': 'List of tag UUIDs to assign'}
    )
    nutrition = fields.Nested(
        RecipeNutritionSchema,
        allow_none=True,
        metadata={'description': 'Nutritional information'}
    )
    change_summary = fields.Str(
        allow_none=True,
        metadata={'description': 'Summary of changes made'}
    )
    
    @validates('name')
    def validate_name(self, value):
        """Validate recipe name."""
        if value is not None and (not value or not value.strip()):
            raise ValidationError("Name cannot be empty")
    
    @validates('ingredients')
    def validate_ingredients(self, value):
        """Validate ingredients list."""
        if value is not None:
            if not value:
                raise ValidationError("Recipe must have at least one ingredient")
            
            # Check for duplicate ingredients
            ingredient_ids = [ing.get('ingredient_product_id') for ing in value]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise ValidationError("Duplicate ingredients are not allowed")
    
    @post_load
    def trim_name(self, data, **kwargs):
        """Trim whitespace from name."""
        if 'name' in data:
            data['name'] = data['name'].strip()
        return data


class RecipeResponseSchema(Schema):
    """Schema for recipe response."""
    
    id = fields.UUID(required=True)
    product_id = fields.UUID(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    version = fields.Int(required=True)
    status = fields.Str(required=True)
    yield_quantity = fields.Decimal(allow_none=True)
    yield_unit = fields.Str(allow_none=True)
    preparation_time = fields.Int(allow_none=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    created_by = fields.UUID(allow_none=True)
    updated_by = fields.UUID(allow_none=True)
    ingredients = fields.Nested(RecipeIngredientSchema, many=True, dump_only=True)
    tags = fields.Nested(RecipeTagSchema, many=True, dump_only=True)
    nutrition = fields.Nested(RecipeNutritionSchema, dump_only=True, allow_none=True)


class RecipeListResponseSchema(Schema):
    """Schema for recipe list response."""
    
    id = fields.UUID(required=True)
    product_id = fields.UUID(required=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    version = fields.Int(required=True)
    status = fields.Str(required=True)
    yield_quantity = fields.Decimal(allow_none=True)
    yield_unit = fields.Str(allow_none=True)
    preparation_time = fields.Int(allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    ingredients_count = fields.Int(dump_only=True)


class PaginationMetaSchema(Schema):
    """Schema for pagination metadata."""
    
    page = fields.Int(required=True, metadata={'description': 'Current page number'})
    per_page = fields.Int(required=True, metadata={'description': 'Items per page'})
    total = fields.Int(required=True, metadata={'description': 'Total number of items'})
    pages = fields.Int(required=True, metadata={'description': 'Total number of pages'})
    has_prev = fields.Bool(required=True, metadata={'description': 'Has previous page'})
    has_next = fields.Bool(required=True, metadata={'description': 'Has next page'})
    prev_num = fields.Int(allow_none=True, metadata={'description': 'Previous page number'})
    next_num = fields.Int(allow_none=True, metadata={'description': 'Next page number'})


class RecipeListSchema(Schema):
    """Schema for paginated recipe list."""
    
    recipes = fields.Nested(RecipeListResponseSchema, many=True, required=True)
    pagination = fields.Nested(PaginationMetaSchema, required=True)


class RecipeValidationResponseSchema(Schema):
    """Schema for recipe validation response."""
    
    is_valid = fields.Bool(required=True)
    validation_errors = fields.List(fields.Str(), required=True)
    recipe_id = fields.UUID(required=True)


class RecipeHierarchyItemSchema(Schema):
    """Schema for recipe hierarchy item."""
    
    ingredient_product_id = fields.UUID(required=True)
    ingredient_name = fields.Str(required=True)
    quantity = fields.Decimal(required=True)
    unit = fields.Str(required=True)
    depth_level = fields.Int(required=True)
    path = fields.List(fields.Str(), required=True)
    
    # Optional product details (when include_product_details=true)
    product_type = fields.Str(allow_none=True)
    product_unit = fields.Str(allow_none=True)
    product_description = fields.Str(allow_none=True)
    
    # Optional scaling information (when target_quantity is provided)
    scaled_for_quantity = fields.Decimal(allow_none=True)
    scaled_for_unit = fields.Str(allow_none=True)
    scale_factor = fields.Decimal(allow_none=True)


class RecipeHierarchyResponseSchema(Schema):
    """Schema for recipe hierarchy response."""
    
    recipe_id = fields.UUID(required=True)
    hierarchy = fields.Nested(RecipeHierarchyItemSchema, many=True, required=True)
    hierarchy_by_depth = fields.Dict(
        keys=fields.Str(), 
        values=fields.Nested(RecipeHierarchyItemSchema, many=True),
        required=True
    )
    max_depth = fields.Int(required=True)
    total_items = fields.Int(required=True)
    scaling_applied = fields.Bool(required=True)
    parameters = fields.Dict(required=True)


class ErrorResponseSchema(Schema):
    """Schema for error response."""
    
    error = fields.Str(required=True, metadata={'description': 'Error message'})
    status_code = fields.Int(required=True, metadata={'description': 'HTTP status code'})
    details = fields.Dict(metadata={'description': 'Additional error details'})


# Query parameter schemas
class RecipeListQuerySchema(Schema):
    """Schema for recipe list query parameters."""
    
    page = fields.Int(
        validate=validate.Range(min=1),
        missing=1,
        metadata={'description': 'Page number (1-based)'}
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        missing=20,
        metadata={'description': 'Items per page (1-100)'}
    )
    status = fields.Str(
        validate=validate.OneOf([s.value for s in RecipeStatus]),
        metadata={'description': 'Filter by recipe status'}
    )
    product_id = fields.UUID(
        metadata={'description': 'Filter by product UUID'}
    )
    include_relationships = fields.Bool(
        missing=False,
        metadata={'description': 'Include ingredients, tags, and nutrition in response'}
    )


class RecipeIngredientUpdateSchema(Schema):
    """Schema for updating individual recipe ingredient."""
    
    quantity = fields.Decimal(
        validate=validate.Range(min=0.001),
        metadata={'description': 'Ingredient quantity'}
    )
    unit = fields.Str(
        validate=validate.OneOf([u.value for u in IngredientUnit]),
        metadata={'description': 'Ingredient unit'}
    )
    sort_order = fields.Int(
        validate=validate.Range(min=0),
        metadata={'description': 'Display order'}
    )
    ingredient_group = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100),
        metadata={'description': 'Ingredient grouping'}
    )
    notes = fields.Str(
        allow_none=True,
        metadata={'description': 'Ingredient notes'}
    )
    is_optional = fields.Bool(
        metadata={'description': 'Whether ingredient is optional'}
    )
    substitute_ingredients = fields.List(
        fields.UUID(),
        allow_none=True,
        metadata={'description': 'Alternative ingredient IDs'}
    )