"""Product API schemas for request/response validation."""
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from uuid import UUID

from ..models.product import Product, ProductCategory, ProductTag, ProductType, ProductUnit


class ProductTypeField(fields.Field):
    """Custom field for ProductType enum."""
    
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value
    
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return ProductType(value)
        except ValueError:
            raise ValidationError(f"Invalid product type: {value}")


class ProductUnitField(fields.Field):
    """Custom field for ProductUnit enum."""
    
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.value
    
    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return ProductUnit(value)
        except ValueError:
            raise ValidationError(f"Invalid product unit: {value}")


class ProductCategorySchema(Schema):
    """Schema for ProductCategory."""
    
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    color = fields.Str(
        allow_none=True,
        validate=validate.Regexp(
            r'^#[0-9A-Fa-f]{6}$',
            error='Color must be a valid hex color code (e.g., #FF0000)'
        )
    )
    created_at = fields.DateTime(dump_only=True)
    
    @validates('name')
    def validate_name(self, value):
        """Validate category name."""
        if not value or not value.strip():
            raise ValidationError("Name cannot be empty")


class ProductTagSchema(Schema):
    """Schema for ProductTag."""
    
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    created_at = fields.DateTime(dump_only=True)
    
    @validates('name')
    def validate_name(self, value):
        """Validate tag name."""
        if not value or not value.strip():
            raise ValidationError("Name cannot be empty")


class ProductCreateSchema(Schema):
    """Schema for creating a product."""
    
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={'description': 'Product name (unique)'}
    )
    type = fields.Str(
        validate=validate.OneOf([t.value for t in ProductType]),
        missing='standard',
        metadata={'description': 'Product type: standard, kit, or semi-product'}
    )
    unit = fields.Str(
        validate=validate.OneOf([u.value for u in ProductUnit]),
        missing='piece',
        metadata={'description': 'Product unit: piece or gram'}
    )
    description = fields.Str(
        allow_none=True,
        validate=validate.Length(max=5000),
        metadata={'description': 'Product description'}
    )
    category_ids = fields.List(
        fields.UUID(),
        missing=[],
        metadata={'description': 'List of category UUIDs to assign'}
    )
    tag_ids = fields.List(
        fields.UUID(),
        missing=[],
        metadata={'description': 'List of tag UUIDs to assign'}
    )
    
    @validates('name')
    def validate_name(self, value):
        """Validate product name."""
        if not value or not value.strip():
            raise ValidationError("Name cannot be empty")
    
    @post_load
    def trim_name(self, data, **kwargs):
        """Trim whitespace from name."""
        if 'name' in data:
            data['name'] = data['name'].strip()
        return data


class ProductUpdateSchema(Schema):
    """Schema for updating a product."""
    
    name = fields.Str(
        validate=validate.Length(min=1, max=255),
        metadata={'description': 'Product name (unique)'}
    )
    type = fields.Str(
        validate=validate.OneOf([t.value for t in ProductType]),
        metadata={'description': 'Product type: standard, kit, or semi-product'}
    )
    unit = fields.Str(
        validate=validate.OneOf([u.value for u in ProductUnit]),
        metadata={'description': 'Product unit: piece or gram'}
    )
    description = fields.Str(
        allow_none=True,
        validate=validate.Length(max=5000),
        metadata={'description': 'Product description'}
    )
    category_ids = fields.List(
        fields.UUID(),
        metadata={'description': 'List of category UUIDs to assign'}
    )
    tag_ids = fields.List(
        fields.UUID(),
        metadata={'description': 'List of tag UUIDs to assign'}
    )
    
    @validates('name')
    def validate_name(self, value):
        """Validate product name."""
        if value is not None and (not value or not value.strip()):
            raise ValidationError("Name cannot be empty")
    
    @post_load
    def trim_name(self, data, **kwargs):
        """Trim whitespace from name."""
        if 'name' in data:
            data['name'] = data['name'].strip()
        return data


class ProductResponseSchema(Schema):
    """Schema for product response."""
    
    id = fields.UUID(required=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    unit = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    created_by = fields.UUID(allow_none=True)
    updated_by = fields.UUID(allow_none=True)
    categories = fields.Nested(ProductCategorySchema, many=True, dump_only=True)
    tags = fields.Nested(ProductTagSchema, many=True, dump_only=True)


class ProductListResponseSchema(Schema):
    """Schema for product list response."""
    
    id = fields.UUID(required=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    unit = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)


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


class ProductListSchema(Schema):
    """Schema for paginated product list."""
    
    products = fields.Nested(ProductListResponseSchema, many=True, required=True)
    pagination = fields.Nested(PaginationMetaSchema, required=True)


class ProductSearchSchema(Schema):
    """Schema for product search request."""
    
    q = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={'description': 'Search query'}
    )
    limit = fields.Int(
        validate=validate.Range(min=1, max=100),
        missing=10,
        metadata={'description': 'Maximum number of results'}
    )
    similarity_threshold = fields.Float(
        validate=validate.Range(min=0.0, max=1.0),
        missing=0.3,
        metadata={'description': 'Minimum similarity threshold (0.0-1.0)'}
    )


class ProductSearchResultSchema(Schema):
    """Schema for product search result."""
    
    id = fields.UUID(required=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    unit = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    similarity_score = fields.Float(required=True, metadata={'description': 'Similarity score (0.0-1.0)'})


class ProductSearchResponseSchema(Schema):
    """Schema for product search response."""
    
    results = fields.Nested(ProductSearchResultSchema, many=True, required=True)
    query = fields.Str(required=True, metadata={'description': 'Original search query'})
    total_results = fields.Int(required=True, metadata={'description': 'Number of results returned'})


class ErrorResponseSchema(Schema):
    """Schema for error response."""
    
    error = fields.Str(required=True, metadata={'description': 'Error message'})
    status_code = fields.Int(required=True, metadata={'description': 'HTTP status code'})
    details = fields.Dict(metadata={'description': 'Additional error details'})


# Query parameter schemas
class ProductListQuerySchema(Schema):
    """Schema for product list query parameters."""
    
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
    type = fields.Str(
        validate=validate.OneOf([t.value for t in ProductType]),
        metadata={'description': 'Filter by product type'}
    )
    unit = fields.Str(
        validate=validate.OneOf([u.value for u in ProductUnit]),
        metadata={'description': 'Filter by product unit'}
    )
    category_id = fields.UUID(
        metadata={'description': 'Filter by category UUID'}
    )
    tag_id = fields.UUID(
        metadata={'description': 'Filter by tag UUID'}
    )
    include_relationships = fields.Bool(
        missing=False,
        metadata={'description': 'Include categories and tags in response'}
    )