"""API documentation information and examples."""

API_INFO = {
    'title': 'Recipe Management Product Service API',
    'version': 'v1.0.0',
    'description': '''
# Product Service API

The Product Service is a microservice that manages product information in the Recipe Management System.
It provides comprehensive product management capabilities including CRUD operations, advanced search,
and category/tag management.

## Features

- **Product Management**: Create, read, update, and delete products
- **Advanced Search**: Fuzzy search with configurable similarity thresholds
- **Filtering**: Filter products by type, unit, category, or tag
- **Categorization**: Flexible product categorization system
- **Tagging**: Tag-based product organization
- **Audit Trail**: Complete change history tracking
- **Caching**: Performance-optimized search caching

## Product Types

- **Standard**: Regular products used as ingredients
- **Kit**: Collections of multiple products
- **Semi Product**: Intermediate products used in other recipes

## Units of Measurement

- **Piece**: Discrete countable items (e.g., 1 apple, 2 eggs)
- **Gram**: Weight-based measurements (e.g., 500g flour)

## Authentication

Currently, the service operates without authentication. User tracking is prepared for future implementation.

## Rate Limiting

The API includes built-in rate limiting to prevent abuse. Standard limits apply to all endpoints.

## Error Handling

All endpoints return consistent error responses with appropriate HTTP status codes and detailed error messages.
''',
    'contact': {
        'name': 'Recipe Management Team',
        'email': 'support@recipemanagement.com'
    },
    'license': {
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/MIT'
    }
}

# Example responses for documentation
EXAMPLE_PRODUCT = {
    'id': '123e4567-e89b-12d3-a456-426614174000',
    'name': 'Premium Olive Oil',
    'type': 'standard',
    'unit': 'gram',
    'description': 'Extra virgin olive oil from Mediterranean olives',
    'created_at': '2023-01-15T10:30:00Z',
    'updated_at': '2023-01-15T10:30:00Z',
    'created_by': '456e7890-e89b-12d3-a456-426614174001',
    'updated_by': '456e7890-e89b-12d3-a456-426614174001',
    'categories': [
        {
            'id': '789e0123-e89b-12d3-a456-426614174002',
            'name': 'Oils & Fats',
            'description': 'Cooking oils and fats',
            'color': '#FFD700',
            'created_at': '2023-01-10T09:00:00Z'
        }
    ],
    'tags': [
        {
            'id': '012e3456-e89b-12d3-a456-426614174003',
            'name': 'premium',
            'created_at': '2023-01-10T09:00:00Z'
        },
        {
            'id': '345e6789-e89b-12d3-a456-426614174004',
            'name': 'mediterranean',
            'created_at': '2023-01-10T09:00:00Z'
        }
    ]
}

EXAMPLE_PRODUCT_LIST = {
    'products': [
        {
            'id': '123e4567-e89b-12d3-a456-426614174000',
            'name': 'Premium Olive Oil',
            'type': 'standard',
            'unit': 'gram',
            'description': 'Extra virgin olive oil',
            'created_at': '2023-01-15T10:30:00Z',
            'updated_at': '2023-01-15T10:30:00Z'
        },
        {
            'id': '456e7890-e89b-12d3-a456-426614174001',
            'name': 'Pasta Kit',
            'type': 'kit',
            'unit': 'piece',
            'description': 'Complete pasta making kit',
            'created_at': '2023-01-16T11:00:00Z',
            'updated_at': '2023-01-16T11:00:00Z'
        }
    ],
    'pagination': {
        'page': 1,
        'per_page': 20,
        'total': 2,
        'pages': 1,
        'has_prev': False,
        'has_next': False,
        'prev_num': None,
        'next_num': None
    }
}

EXAMPLE_SEARCH_RESPONSE = {
    'results': [
        {
            'id': '123e4567-e89b-12d3-a456-426614174000',
            'name': 'Premium Olive Oil',
            'type': 'standard',
            'unit': 'gram',
            'description': 'Extra virgin olive oil',
            'similarity_score': 0.95
        },
        {
            'id': '456e7890-e89b-12d3-a456-426614174001',
            'name': 'Olive Paste',
            'type': 'standard',
            'unit': 'gram',
            'description': 'Mediterranean olive paste',
            'similarity_score': 0.82
        }
    ],
    'suggestions': ['olive oil', 'olive paste', 'olives'],
    'query': 'olive',
    'normalized_query': 'olive',
    'total_results': 2,
    'search_time_ms': 45,
    'filters_applied': {}
}

EXAMPLE_ERROR_RESPONSE = {
    'error': 'Product with name \'Duplicate Product\' already exists',
    'status_code': 409,
    'details': {
        'field': 'name',
        'message': 'This name is already taken'
    }
}

# API endpoint examples
API_EXAMPLES = {
    'create_product': {
        'summary': 'Create a new product',
        'description': 'Creates a new product with the provided information',
        'request_body': {
            'name': 'Premium Olive Oil',
            'type': 'standard',
            'unit': 'gram',
            'description': 'Extra virgin olive oil from Mediterranean olives',
            'category_ids': ['789e0123-e89b-12d3-a456-426614174002'],
            'tag_ids': ['012e3456-e89b-12d3-a456-426614174003']
        },
        'response': EXAMPLE_PRODUCT
    },
    'search_products': {
        'summary': 'Search products with fuzzy matching',
        'description': 'Performs fuzzy search on product names with similarity scoring',
        'query_params': {
            'q': 'olive',
            'limit': 10,
            'similarity_threshold': 0.3
        },
        'response': EXAMPLE_SEARCH_RESPONSE
    },
    'advanced_search': {
        'summary': 'Advanced search with filters',
        'description': 'Performs advanced search with multiple filters and suggestions',
        'query_params': {
            'q': 'oil',
            'type': 'standard',
            'unit': 'gram',
            'limit': 20,
            'similarity_threshold': 0.3,
            'include_suggestions': True
        },
        'response': EXAMPLE_SEARCH_RESPONSE
    }
}