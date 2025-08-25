# Recipe Management Service

A comprehensive microservice for managing recipes and their hierarchical ingredient relationships in the Recipe Management System. Built with Flask, SQLAlchemy, and PostgreSQL.

## Features

- **Recipe Management**: Complete CRUD operations for recipes
- **Hierarchical Ingredients**: Support for nested recipes with semi-products
- **Circular Dependency Prevention**: Automatic detection and prevention of recipe loops
- **Advanced Hierarchy Queries**: Recursive ingredient expansion with depth control
- **Quantity Scaling**: Proportional ingredient scaling for different production volumes
- **Recipe Analysis**: Complexity metrics and performance insights
- **Product Integration**: Seamless communication with Product Service
- **Comprehensive Testing**: Unit, integration, and performance tests
- **OpenAPI Documentation**: Interactive API documentation with Swagger UI

## Architecture

### Technology Stack
- **Framework**: Flask 2.3+ with Flask-RESTful
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0
- **API Documentation**: Flask-SMOREST (OpenAPI 3.0)
- **Validation**: Marshmallow schemas
- **Testing**: Pytest with coverage reporting
- **Caching**: Redis for performance optimization
- **Logging**: Structured logging with structlog

### Database Schema
- **recipes**: Main recipe information with versioning
- **recipe_ingredients**: Ingredient relationships with quantities
- **recipe_dependencies**: Hierarchical dependency tracking
- **recipe_versions**: Complete version history
- **recipe_nutrition**: Nutritional information
- **recipe_tags**: Flexible tagging system
- **recipe_audit**: Comprehensive change tracking

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 6+
- Product Service running (for integration)

### Installation

1. **Clone and Setup**
   ```bash
   cd services/recipe-service
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Create database
   createdb recipe_service_db
   
   # Run migrations
   flask db upgrade
   
   # Optional: Load sample data
   python scripts/load_sample_data.py
   ```

3. **Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit configuration
   nano .env
   ```

4. **Run Service**
   ```bash
   # Development mode
   flask run --host=0.0.0.0 --port=8002
   
   # Production mode
   gunicorn -w 4 -b 0.0.0.0:8002 app:create_app()
   ```

### API Documentation
- **Swagger UI**: http://localhost:8002/swagger-ui
- **OpenAPI Spec**: http://localhost:8002/openapi.json
- **Health Check**: http://localhost:8002/health

## API Endpoints

### Core Recipe Operations

#### Create Recipe
```http
POST /api/v1/recipes/
Content-Type: application/json

{
  "product_id": "uuid",
  "name": "Chocolate Chip Cookies",
  "description": "Classic homemade cookies",
  "status": "draft",
  "yield_quantity": 24,
  "yield_unit": "piece",
  "preparation_time": 45,
  "ingredients": [
    {
      "ingredient_product_id": "uuid",
      "quantity": 250.0,
      "unit": "gram",
      "ingredient_group": "Dry Ingredients",
      "sort_order": 1
    }
  ]
}
```

#### Get Recipe
```http
GET /api/v1/recipes/{recipe_id}
```

#### Update Recipe
```http
PUT /api/v1/recipes/{recipe_id}
Content-Type: application/json

{
  "name": "Updated Recipe Name",
  "status": "active"
}
```

#### Delete Recipe
```http
DELETE /api/v1/recipes/{recipe_id}
```

### Advanced Features

#### Recipe Hierarchy
```http
GET /api/v1/recipes/{recipe_id}/hierarchy?max_depth=10&target_quantity=1000&target_unit=gram
```

**Response:**
```json
{
  "recipe_id": "uuid",
  "hierarchy": [
    {
      "ingredient_product_id": "uuid",
      "ingredient_name": "Flour",
      "quantity": 500.0,
      "unit": "gram",
      "depth_level": 1,
      "path": ["ingredient_uuid"],
      "product_type": "standard",
      "scaled_for_quantity": 1000.0,
      "scale_factor": 2.0
    }
  ],
  "hierarchy_by_depth": {
    "1": [...],
    "2": [...]
  },
  "max_depth": 3,
  "total_items": 15,
  "scaling_applied": true
}
```

#### Recipe Analysis
```http
GET /api/v1/recipes/{recipe_id}/analysis
```

**Response:**
```json
{
  "recipe_id": "uuid",
  "complexity_metrics": {
    "ingredient_count": 7,
    "hierarchy_depth": 3,
    "total_ingredients_expanded": 15,
    "complexity_score": 22,
    "complexity_level": "moderate",
    "optional_ingredients": 1,
    "required_ingredients": 6
  },
  "dependencies": [...],
  "hierarchy_analysis": {
    "unit_distribution": {
      "gram": {"count": 12, "total_quantity": 1250.0},
      "piece": {"count": 3, "total_quantity": 5}
    },
    "depth_distribution": {
      "1": 7,
      "2": 6,
      "3": 2
    }
  },
  "performance_insights": [
    {
      "type": "info",
      "message": "Recipe has good organizational structure",
      "recommendation": "Consider adding more ingredient groups"
    }
  ]
}
```

#### Find Recipes Using Product
```http
GET /api/v1/recipes/product/{product_id}
```

#### Recipe Validation
```http
GET /api/v1/recipes/{recipe_id}/validate
```

### List Operations

#### Get All Recipes
```http
GET /api/v1/recipes/?page=1&per_page=20&status=active&include_relationships=true
```

#### Get Recipe Tags
```http
GET /api/v1/recipes/tags
```

### Ingredient Management

#### Update Recipe Ingredient
```http
PUT /api/v1/recipes/{recipe_id}/ingredients/{ingredient_id}
Content-Type: application/json

{
  "quantity": 150.0,
  "notes": "Updated ingredient notes",
  "is_optional": true
}
```

#### Delete Recipe Ingredient
```http
DELETE /api/v1/recipes/{recipe_id}/ingredients/{ingredient_id}
```

## Business Rules

### Recipe Validation
- Recipes must have at least one ingredient
- At least one ingredient must be required (non-optional)
- Ingredient quantities must be positive
- Product IDs must exist in Product Service
- No duplicate ingredients in the same recipe

### Circular Dependency Prevention
- Recipes cannot reference themselves directly or indirectly
- Database triggers prevent circular dependencies
- Real-time validation during recipe creation/updates
- Path tracking to detect complex cycles (A→B→C→A)

### Hierarchy Management
- Maximum depth limit (default: 10 levels)
- Automatic quantity scaling for nested recipes
- Performance optimization for large hierarchies
- Caching for frequently accessed hierarchical data

### Units and Scaling
- Support for piece and gram measurements
- Mixed units within recipes
- Proportional scaling based on yield quantities
- Automatic unit conversion where applicable

## Testing

### Test Structure
```
tests/
├── unit/                 # Fast, isolated tests
│   ├── test_recipe_models.py
│   ├── test_recipe_repository.py
│   └── test_circular_dependencies.py
├── integration/          # API and database tests
│   └── test_recipe_api.py
├── performance/          # Performance and load tests
│   └── test_hierarchy_performance.py
└── conftest.py          # Test configuration
```

### Running Tests

```bash
# All tests
python run_tests.py all

# Specific test types
python run_tests.py unit           # Unit tests only
python run_tests.py integration    # Integration tests only
python run_tests.py performance    # Performance tests only
python run_tests.py fast          # Unit + Integration (quick)

# With coverage
python run_tests.py coverage

# Specific test file
python run_tests.py unit --file tests/unit/test_recipe_models.py

# Verbose output
python run_tests.py all --verbose

# Parallel execution
python run_tests.py fast --parallel
```

### Test Categories
- **Unit Tests** (`@pytest.mark.unit`): Model validation, business logic
- **Integration Tests** (`@pytest.mark.integration`): API endpoints, database operations  
- **Performance Tests** (`@pytest.mark.performance`): Query performance, scalability
- **Slow Tests** (`@pytest.mark.slow`): Stress tests (usually skipped)

### Coverage Requirements
- Minimum 80% code coverage
- 100% coverage for critical business logic
- HTML coverage reports generated in `htmlcov/`

## Performance Considerations

### Database Optimization
- Composite indexes for common query patterns
- Recursive CTEs for hierarchical queries
- Connection pooling and query optimization
- Proper foreign key constraints

### Caching Strategy
- Redis caching for frequently accessed data
- Recipe hierarchy caching with TTL
- Product information caching
- Cache invalidation on updates

### Query Performance
- Depth limiting for hierarchical queries (max 20 levels)
- Batch operations for multiple product lookups
- Pagination for large result sets
- Database function optimization

### Scalability
- Stateless service design
- Horizontal scaling capability
- Efficient memory usage
- Connection pooling

## Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/recipe_db
DATABASE_POOL_SIZE=10
DATABASE_POOL_TIMEOUT=30

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# Service Configuration
FLASK_ENV=production
LOG_LEVEL=INFO
API_VERSION=v1
MAX_INGREDIENTS_PER_RECIPE=100

# External Services
PRODUCT_SERVICE_URL=http://localhost:8001
PRODUCT_SERVICE_TIMEOUT=30
PRODUCT_SERVICE_RETRIES=3

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Production Configuration
```python
# config/production.py
class ProductionConfig:
    DEBUG = False
    TESTING = False
    DATABASE_URL = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    LOG_LEVEL = logging.INFO
    
    # Performance tuning
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'max_overflow': 30
    }
```

## Monitoring and Logging

### Structured Logging
```python
import structlog

logger = structlog.get_logger("recipe_service")

logger.info(
    "Recipe created successfully",
    recipe_id=recipe.id,
    product_id=recipe.product_id,
    ingredient_count=len(recipe.ingredients)
)
```

### Health Checks
- Database connectivity check
- Product Service integration check
- Redis connectivity check
- Service-specific health metrics

### Metrics Collection
- Request/response times
- Error rates and types
- Recipe complexity distribution
- Database query performance
- Cache hit/miss ratios

## Error Handling

### Custom Exceptions
```python
from app.utils.exceptions import (
    RecipeNotFoundError,
    RecipeValidationError,
    CircularDependencyError,
    MaxDepthExceededError
)
```

### Error Response Format
```json
{
  "error": "Recipe validation failed",
  "status_code": 400,
  "details": {
    "field": "ingredients",
    "message": "Recipe must have at least one ingredient"
  }
}
```

## Development

### Code Quality
- **Black**: Code formatting
- **Flake8**: Linting and style checks
- **MyPy**: Type checking
- **Pre-commit**: Git hooks for quality

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Adding New Features

1. **Models**: Add/modify SQLAlchemy models in `app/models/`
2. **Repository**: Implement data access in `app/services/`
3. **API**: Create endpoints in `app/resources/`
4. **Schemas**: Define validation in `app/schemas/`
5. **Tests**: Add comprehensive tests
6. **Documentation**: Update API documentation

## Troubleshooting

### Common Issues

1. **Circular Dependency Error**
   - Check recipe ingredient relationships
   - Verify database triggers are enabled
   - Review hierarchy depth

2. **Performance Issues**
   - Check query complexity and depth limits
   - Verify database indexes
   - Monitor cache hit rates

3. **Product Service Integration**
   - Verify service connectivity
   - Check authentication/authorization
   - Review timeout settings

### Debug Mode
```bash
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
flask run
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with tests
4. Run quality checks (`pre-commit run --all-files`)
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Maintain test coverage above 80%

## License

This project is part of the Recipe Management System. See LICENSE file for details.

## Support

For support and questions:
- Create an issue in the project repository
- Contact the development team
- Check the troubleshooting section

---

**Recipe Management Service** - Building hierarchical recipe management with performance and reliability in mind.