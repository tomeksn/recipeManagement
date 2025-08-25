# Product Service

The Product Service is a microservice component of the Recipe Management System that handles all product-related operations including CRUD operations, advanced search, categorization, and audit trails.

## Features

- **Product Management**: Complete CRUD operations for products
- **Advanced Search**: Fuzzy search with similarity scoring and caching
- **Filtering**: Filter products by type, unit, category, or tag
- **Categorization**: Flexible category system with color coding
- **Tagging**: Tag-based product organization
- **Audit Trail**: Complete change history tracking
- **OpenAPI Documentation**: Comprehensive API documentation
- **High Test Coverage**: Unit and integration tests

## Architecture

### Technology Stack

- **Python 3.11+**: Core programming language
- **Flask 2.3+**: Web framework
- **SQLAlchemy 2.0**: ORM with PostgreSQL
- **Flask-SMOREST**: OpenAPI documentation
- **Marshmallow**: Data serialization and validation
- **pytest**: Testing framework
- **Docker**: Containerization

### Database Schema

The service uses PostgreSQL with the following main entities:

- **Products**: Core product information
- **Product Categories**: Flexible categorization system
- **Product Tags**: Tag-based organization
- **Product Audit**: Change tracking
- **Search Cache**: Performance optimization

## API Endpoints

### Products

- `GET /api/v1/products/` - List products with pagination and filtering
- `POST /api/v1/products/` - Create a new product
- `GET /api/v1/products/{id}` - Get a single product
- `PUT /api/v1/products/{id}` - Update a product
- `DELETE /api/v1/products/{id}` - Delete a product

### Search

- `GET /api/v1/products/search` - Basic fuzzy search
- `GET /api/v1/search/` - Advanced search with filters
- `GET /api/v1/search/suggestions` - Search suggestions for autocomplete
- `GET /api/v1/search/popular` - Popular search terms

### Categories & Tags

- `GET /api/v1/products/categories` - List all categories
- `GET /api/v1/products/tags` - List all tags

### Health & Maintenance

- `GET /health` - Health check endpoint
- `DELETE /api/v1/search/cache/cleanup` - Clean expired search cache

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose
- Redis (for caching)

### Installation

1. **Clone the repository**
   ```bash
   cd services/product-service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Make sure PostgreSQL is running
   # Database schema will be created automatically
   ```

### Running the Service

#### Development Mode

```bash
# Run directly with Flask
python app.py

# Or with gunicorn
gunicorn --bind 0.0.0.0:8001 --reload app:create_app()
```

#### Docker Mode

```bash
# Build and run with Docker
docker build -t product-service .
docker run -p 8001:8001 product-service

# Or use Docker Compose (from project root)
docker-compose up product-service
```

### Testing

#### Run All Tests

```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py
```

#### Specific Test Types

```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# With coverage report
python run_tests.py --coverage

# Specific test pattern
python run_tests.py -k "test_create_product"
```

#### Code Quality Checks

```bash
# Format code
black app tests

# Type checking
mypy app

# Linting
flake8 app tests

# All checks
python run_tests.py  # Includes quality checks
```

## API Documentation

### Swagger UI

Once the service is running, visit:
- http://localhost:8001/docs/swagger for interactive API documentation
- http://localhost:8001/docs/redoc for alternative documentation

### Example Usage

#### Create a Product

```bash
curl -X POST http://localhost:8001/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Premium Olive Oil",
    "type": "standard",
    "unit": "gram",
    "description": "Extra virgin olive oil from Mediterranean olives"
  }'
```

#### Search Products

```bash
# Basic search
curl "http://localhost:8001/api/v1/products/search?q=olive&limit=10"

# Advanced search with filters
curl "http://localhost:8001/api/v1/search/?q=oil&type=standard&unit=gram&limit=20"
```

#### Get Products with Pagination

```bash
curl "http://localhost:8001/api/v1/products/?page=1&per_page=20&type=standard"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_HOST` | PostgreSQL host | `localhost` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |
| `DATABASE_NAME` | Database name | `recipe_management_dev` |
| `DATABASE_USER` | Database user | `recipe_user` |
| `DATABASE_PASSWORD` | Database password | Required |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `FLASK_ENV` | Flask environment | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Database Configuration

The service expects PostgreSQL with the following schema: `product_service`

Required PostgreSQL extensions:
- `pg_trgm` (for fuzzy search)
- `btree_gin` (for indexing)

## Performance Considerations

### Search Optimization

- Fuzzy search uses PostgreSQL's full-text search and trigram matching
- Search results are cached in Redis for 5 minutes
- Database indexes are optimized for common query patterns

### Caching Strategy

- Search results cached by query hash
- Category and tag lists cached (small datasets)
- Database connection pooling enabled

### Scaling Recommendations

- Use read replicas for search operations
- Implement Redis clustering for high availability
- Consider Elasticsearch for very large product catalogs

## Monitoring

### Health Checks

- `/health` endpoint for container orchestration
- Database connectivity checks
- Cache availability verification

### Logging

- Structured logging with request correlation IDs
- Performance metrics for search operations
- Error tracking with detailed context

### Metrics

Key metrics to monitor:
- Search response times
- Database query performance
- Cache hit rates
- Error rates by endpoint

## Contributing

### Code Style

- Use Black for code formatting
- Follow PEP 8 guidelines
- Type hints required for public APIs
- Comprehensive docstrings

### Testing Requirements

- Minimum 80% test coverage
- Unit tests for business logic
- Integration tests for API endpoints
- Performance tests for search functionality

### Pull Request Process

1. Create feature branch from main
2. Implement changes with tests
3. Run full test suite
4. Update documentation if needed
5. Submit pull request with description

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection settings
psql -h localhost -U recipe_user -d recipe_management_dev
```

#### Search Not Working

```bash
# Check required PostgreSQL extensions
psql -d recipe_management_dev -c "SELECT * FROM pg_extension WHERE extname IN ('pg_trgm', 'btree_gin');"
```

#### Performance Issues

```bash
# Check database indexes
psql -d recipe_management_dev -c "\di product_service.*"

# Monitor slow queries
# Enable log_min_duration_statement in postgresql.conf
```

### Debugging

Enable debug logging:

```bash
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
python app.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Create an issue in the project repository
- Contact the development team
- Check the API documentation at `/docs/swagger`