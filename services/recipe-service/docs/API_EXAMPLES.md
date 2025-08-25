# Recipe Service API Examples

This document provides comprehensive examples of using the Recipe Service API for common scenarios.

## Table of Contents
- [Authentication](#authentication)
- [Basic Recipe Operations](#basic-recipe-operations)
- [Hierarchical Recipes](#hierarchical-recipes)
- [Recipe Analysis](#recipe-analysis)
- [Bulk Operations](#bulk-operations)
- [Error Handling](#error-handling)

## Authentication

```bash
# All requests should include appropriate headers
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-token" \
     http://localhost:8002/api/v1/recipes/
```

## Basic Recipe Operations

### Create a Simple Recipe

```bash
curl -X POST http://localhost:8002/api/v1/recipes/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Chocolate Chip Cookies",
    "description": "Classic homemade chocolate chip cookies",
    "status": "draft",
    "yield_quantity": 24,
    "yield_unit": "piece",
    "preparation_time": 45,
    "ingredients": [
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440002",
        "quantity": 250.0,
        "unit": "gram",
        "ingredient_group": "Dry Ingredients",
        "sort_order": 1,
        "notes": "All-purpose flour"
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440003",
        "quantity": 150.0,
        "unit": "gram",
        "ingredient_group": "Dry Ingredients",
        "sort_order": 2
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440004",
        "quantity": 125.0,
        "unit": "gram",
        "ingredient_group": "Wet Ingredients",
        "sort_order": 3
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440005",
        "quantity": 2,
        "unit": "piece",
        "ingredient_group": "Wet Ingredients",
        "sort_order": 4
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440006",
        "quantity": 200.0,
        "unit": "gram",
        "ingredient_group": "Mix-ins",
        "sort_order": 5,
        "is_optional": true,
        "notes": "Dark chocolate chips preferred"
      }
    ],
    "tag_ids": ["550e8400-e29b-41d4-a716-446655440007"],
    "nutrition": {
      "calories": 180.0,
      "protein": 3.5,
      "carbohydrates": 24.0,
      "fat": 8.5,
      "calculation_method": "manual"
    }
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "product_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Chocolate Chip Cookies",
  "description": "Classic homemade chocolate chip cookies",
  "version": 1,
  "status": "draft",
  "yield_quantity": 24.0,
  "yield_unit": "piece",
  "preparation_time": 45,
  "created_at": "2025-01-24T10:30:00Z",
  "updated_at": "2025-01-24T10:30:00Z",
  "ingredients": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440002",
      "quantity": 250.0,
      "unit": "gram",
      "sort_order": 1,
      "ingredient_group": "Dry Ingredients",
      "notes": "All-purpose flour",
      "is_optional": false
    }
  ]
}
```

### Get Recipe with Full Details

```bash
curl http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440010
```

### Update Recipe Status

```bash
curl -X PUT http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440010 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active",
    "change_summary": "Recipe tested and approved for production"
  }'
```

### List Recipes with Filters

```bash
# Get active recipes with pagination
curl "http://localhost:8002/api/v1/recipes/?status=active&page=1&per_page=10&include_relationships=true"

# Filter by product
curl "http://localhost:8002/api/v1/recipes/?product_id=550e8400-e29b-41d4-a716-446655440001"
```

## Hierarchical Recipes

### Create a Semi-Product Recipe

```bash
# First, create a recipe for cookie dough (semi-product)
curl -X POST http://localhost:8002/api/v1/recipes/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440100",
    "name": "Cookie Dough Base",
    "description": "Basic cookie dough for various cookie types",
    "status": "active",
    "yield_quantity": 1000.0,
    "yield_unit": "gram",
    "preparation_time": 15,
    "ingredients": [
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440002",
        "quantity": 400.0,
        "unit": "gram",
        "ingredient_group": "Base",
        "sort_order": 1
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440003",
        "quantity": 200.0,
        "unit": "gram",
        "ingredient_group": "Base",
        "sort_order": 2
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440004",
        "quantity": 250.0,
        "unit": "gram",
        "ingredient_group": "Base",
        "sort_order": 3
      }
    ]
  }'
```

### Create Recipe Using Semi-Product

```bash
# Create chocolate chip cookies using the cookie dough base
curl -X POST http://localhost:8002/api/v1/recipes/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440101",
    "name": "Premium Chocolate Chip Cookies",
    "description": "Cookies made with our signature cookie dough base",
    "status": "active",
    "yield_quantity": 24,
    "yield_unit": "piece",
    "preparation_time": 30,
    "ingredients": [
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440100",
        "quantity": 800.0,
        "unit": "gram",
        "ingredient_group": "Base",
        "sort_order": 1,
        "notes": "Use fresh cookie dough base"
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440006",
        "quantity": 200.0,
        "unit": "gram",
        "ingredient_group": "Mix-ins",
        "sort_order": 2
      },
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440007",
        "quantity": 5.0,
        "unit": "gram",
        "ingredient_group": "Flavoring",
        "sort_order": 3,
        "is_optional": true
      }
    ]
  }'
```

### Get Recipe Hierarchy

```bash
# Get full hierarchy expansion
curl "http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/hierarchy?max_depth=10&include_product_details=true"
```

**Response:**
```json
{
  "recipe_id": "550e8400-e29b-41d4-a716-446655440101",
  "hierarchy": [
    {
      "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440100",
      "ingredient_name": "Cookie Dough Base",
      "quantity": 800.0,
      "unit": "gram",
      "depth_level": 1,
      "path": ["550e8400-e29b-41d4-a716-446655440100"],
      "product_type": "semi_product"
    },
    {
      "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440002",
      "ingredient_name": "All-Purpose Flour",
      "quantity": 320.0,
      "unit": "gram",
      "depth_level": 2,
      "path": ["550e8400-e29b-41d4-a716-446655440100", "550e8400-e29b-41d4-a716-446655440002"],
      "product_type": "standard"
    }
  ],
  "hierarchy_by_depth": {
    "1": [
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440100",
        "ingredient_name": "Cookie Dough Base",
        "quantity": 800.0,
        "unit": "gram",
        "depth_level": 1
      }
    ],
    "2": [
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440002",
        "ingredient_name": "All-Purpose Flour",
        "quantity": 320.0,
        "unit": "gram",
        "depth_level": 2
      }
    ]
  },
  "max_depth": 2,
  "total_items": 8,
  "scaling_applied": false
}
```

### Get Scaled Recipe Hierarchy

```bash
# Scale recipe for 100 cookies instead of 24
curl "http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/hierarchy?target_quantity=100&target_unit=piece"
```

## Recipe Analysis

### Get Recipe Complexity Analysis

```bash
curl http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/analysis
```

**Response:**
```json
{
  "recipe_id": "550e8400-e29b-41d4-a716-446655440101",
  "complexity_metrics": {
    "ingredient_count": 3,
    "hierarchy_depth": 2,
    "total_ingredients_expanded": 8,
    "complexity_score": 18,
    "complexity_level": "moderate",
    "ingredient_groups": 3,
    "optional_ingredients": 1,
    "required_ingredients": 2
  },
  "dependencies": [
    {
      "parent_recipe_id": "550e8400-e29b-41d4-a716-446655440101",
      "child_product_id": "550e8400-e29b-41d4-a716-446655440100",
      "dependency_type": "ingredient",
      "depth_level": 1
    }
  ],
  "hierarchy_analysis": {
    "total_expanded_ingredients": 8,
    "unit_distribution": {
      "gram": {
        "count": 7,
        "total_quantity": 1375.0
      },
      "piece": {
        "count": 1,
        "total_quantity": 1
      }
    },
    "depth_distribution": {
      "1": 3,
      "2": 5
    }
  },
  "performance_insights": [
    {
      "type": "info",
      "message": "Recipe has good organizational structure",
      "recommendation": "Ingredient groups help with organization"
    },
    {
      "type": "info",
      "message": "Moderate complexity recipe",
      "recommendation": "Consider breaking down complex ingredients if needed"
    }
  ],
  "analysis_timestamp": "2025-01-24T11:15:30.123456Z"
}
```

### Validate Recipe

```bash
curl http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/validate
```

**Response:**
```json
{
  "is_valid": true,
  "validation_errors": [],
  "recipe_id": "550e8400-e29b-41d4-a716-446655440101"
}
```

### Find Recipes Using Specific Product

```bash
# Find all recipes that use flour as an ingredient
curl http://localhost:8002/api/v1/recipes/product/550e8400-e29b-41d4-a716-446655440002
```

**Response:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440002",
  "recipes": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "name": "Cookie Dough Base",
      "status": "active",
      "usage_details": {
        "quantity": 400.0,
        "unit": "gram",
        "is_optional": false,
        "ingredient_group": "Base",
        "notes": null
      }
    }
  ],
  "total_count": 1
}
```

## Bulk Operations

### Create Multiple Recipes

```bash
# Note: The API doesn't have a native bulk create endpoint,
# but you can use parallel requests or batch processing

# Create recipes in sequence
for recipe in recipe1.json recipe2.json recipe3.json; do
  curl -X POST http://localhost:8002/api/v1/recipes/ \
    -H "Content-Type: application/json" \
    -d @$recipe
done
```

### Batch Update Recipe Status

```bash
# Update multiple recipes to active status
recipe_ids=("550e8400-e29b-41d4-a716-446655440101" "550e8400-e29b-41d4-a716-446655440102")

for id in "${recipe_ids[@]}"; do
  curl -X PUT http://localhost:8002/api/v1/recipes/$id \
    -H "Content-Type: application/json" \
    -d '{"status": "active"}'
done
```

## Advanced Ingredient Management

### Update Recipe Ingredient

```bash
curl -X PUT http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/ingredients/550e8400-e29b-41d4-a716-446655440020 \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 180.0,
    "notes": "Reduced quantity after testing",
    "is_optional": false,
    "ingredient_group": "Mix-ins"
  }'
```

### Delete Recipe Ingredient

```bash
curl -X DELETE http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/ingredients/550e8400-e29b-41d4-a716-446655440020
```

## Recipe Tags Management

### Get All Tags

```bash
curl http://localhost:8002/api/v1/recipes/tags
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440007",
    "name": "dessert",
    "color": "#FF69B4",
    "description": "Sweet dessert recipes",
    "created_at": "2025-01-24T09:00:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440008",
    "name": "quick",
    "color": "#90EE90",
    "description": "Quick preparation recipes",
    "created_at": "2025-01-24T09:00:00Z"
  }
]
```

## Error Handling

### Validation Errors

```bash
# Attempt to create recipe with invalid data
curl -X POST http://localhost:8002/api/v1/recipes/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "invalid-uuid",
    "name": "",
    "ingredients": []
  }'
```

**Error Response:**
```json
{
  "error": "Validation failed",
  "status_code": 400,
  "details": {
    "product_id": ["Not a valid UUID."],
    "name": ["Name cannot be empty"],
    "ingredients": ["Recipe must have at least one ingredient"]
  }
}
```

### Circular Dependency Error

```bash
# Attempt to create circular dependency
curl -X POST http://localhost:8002/api/v1/recipes/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "Flour Recipe",
    "ingredients": [
      {
        "ingredient_product_id": "550e8400-e29b-41d4-a716-446655440100",
        "quantity": 500.0,
        "unit": "gram"
      }
    ]
  }'
```

**Error Response:**
```json
{
  "error": "Circular dependency detected",
  "status_code": 409,
  "details": {
    "message": "Cannot add ingredient that would create a cycle",
    "dependency_path": ["550e8400-e29b-41d4-a716-446655440100", "550e8400-e29b-41d4-a716-446655440002"]
  }
}
```

### Resource Not Found

```bash
curl http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440999
```

**Error Response:**
```json
{
  "error": "Recipe with ID 550e8400-e29b-41d4-a716-446655440999 not found",
  "status_code": 404
}
```

## Performance Testing

### Large Hierarchy Query

```bash
# Test performance with depth limiting
time curl "http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/hierarchy?max_depth=5"

# Compare with unlimited depth (be careful with complex recipes)
time curl "http://localhost:8002/api/v1/recipes/550e8400-e29b-41d4-a716-446655440101/hierarchy?max_depth=20"
```

### Pagination Performance

```bash
# Test large result sets with pagination
time curl "http://localhost:8002/api/v1/recipes/?page=1&per_page=50&include_relationships=true"
```

## Integration Examples

### With Product Service

```bash
# Ensure product exists before creating recipe
PRODUCT_ID="550e8400-e29b-41d4-a716-446655440001"

# Check product exists in Product Service
curl http://localhost:8001/api/v1/products/$PRODUCT_ID

# If product exists, create recipe
curl -X POST http://localhost:8002/api/v1/recipes/ \
  -H "Content-Type: application/json" \
  -d "{\"product_id\": \"$PRODUCT_ID\", \"name\": \"Test Recipe\", \"ingredients\": [...]}"
```

### Health Check Integration

```bash
# Check service health
curl http://localhost:8002/health

# Expected response
{
  "status": "healthy",
  "service": "recipe-service",
  "version": "v1.0.0",
  "dependencies": {
    "database": "connected",
    "product_service": "connected"
  }
}
```

## Monitoring and Debugging

### Request Tracing

```bash
# Add correlation ID for request tracing
curl -H "X-Correlation-ID: req-12345" \
     -H "Content-Type: application/json" \
     http://localhost:8002/api/v1/recipes/
```

### Performance Monitoring

```bash
# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8002/api/v1/recipes/

# curl-format.txt content:
#     time_namelookup:  %{time_namelookup}\n
#        time_connect:  %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#    time_pretransfer:  %{time_pretransfer}\n
#       time_redirect:  %{time_redirect}\n
#  time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#          time_total:  %{time_total}\n
```

This concludes the comprehensive API examples for the Recipe Service. These examples cover all major functionality and should help developers integrate with the service effectively.