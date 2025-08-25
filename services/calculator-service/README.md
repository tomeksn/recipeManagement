# Calculator Service

High-performance recipe calculation service for the Recipe Management System. Provides scaling calculations, unit conversions, and hierarchical recipe expansion with Redis caching for optimal performance.

## Features

- **Recipe Scaling**: Scale recipes to any target quantity or weight
- **Unit Handling**: Support for piece and gram measurements with mixed units
- **Hierarchical Expansion**: Expand semi-products to show sub-recipe ingredients
- **Precision Control**: Configurable rounding and decimal precision
- **Performance Optimization**: Redis caching with configurable TTL
- **Batch Operations**: Calculate multiple recipes in single request

## Calculation Types

### Piece-Based Scaling
For products measured in pieces (e.g., cookies, loaves):
- All ingredients scaled by multiplication factor
- Target quantity: pieces → scale factor = target / yield
- Example: Recipe yields 24 cookies, scale for 100 → factor = 100/24 = 4.17

### Weight-Based Scaling  
For products measured by weight (e.g., dough, sauce):
- All ingredients scaled proportionally
- Target weight: grams → scale factor = target / yield_weight
- Example: Recipe yields 1000g, scale for 500g → factor = 0.5

### Mixed Unit Support
Recipes can contain both piece and gram ingredients:
- Each ingredient scaled according to its unit
- Maintains proportional relationships
- Results formatted with appropriate precision

## API Endpoints

### Calculate Recipe
```http
POST /api/v1/calculations/calculate
```

Calculate ingredient quantities for a recipe.

**Request Body:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_quantity": 100,
  "target_unit": "piece",
  "include_hierarchy": false,
  "max_depth": 5,
  "precision": 3
}
```

**Response:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Chocolate Chip Cookies",
  "target_quantity": 100,
  "target_unit": "piece",
  "scale_factor": 4.17,
  "original_yield": 24,
  "original_yield_unit": "piece",
  "ingredients": [
    {
      "product_id": "660e8400-e29b-41d4-a716-446655440001",
      "product_name": "Flour",
      "original_quantity": 500,
      "calculated_quantity": 2085,
      "unit": "gram",
      "order": 1
    }
  ],
  "calculation_metadata": {
    "include_hierarchy": false,
    "max_depth": 5,
    "precision": 3,
    "ingredient_count": 5,
    "algorithm_version": "v1.0"
  },
  "cached": false,
  "calculation_time_ms": 15.2
}
```

### Batch Calculate
```http
POST /api/v1/calculations/calculate/batch
```

Calculate multiple recipes in a single request.

### Calculation History
```http
GET /api/v1/calculations/history?product_id=UUID&limit=50&offset=0
```

Get calculation history with optional filtering.

### Cache Management
```http
GET /api/v1/calculations/cache/stats
POST /api/v1/calculations/cache/clear
```

Monitor and manage calculation cache.

## Configuration

Environment variables for configuration:

```bash
# Service Configuration
FLASK_ENV=development
PORT=8003
SECRET_KEY=your-secret-key

# Redis Configuration
REDIS_URL=redis://localhost:6379/2
CACHE_TTL=3600
CALCULATION_CACHE_TTL=1800
ENABLE_RESULT_CACHING=true

# Recipe Service Integration
RECIPE_SERVICE_URL=http://localhost:8002
RECIPE_SERVICE_TIMEOUT=30
RECIPE_SERVICE_RETRIES=3

# Calculation Parameters
PRECISION_DECIMAL_PLACES=3
MAX_SCALE_FACTOR=1000.0
MIN_SCALE_FACTOR=0.001
MAX_INGREDIENTS_PER_CALCULATION=1000

# CORS
CORS_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

## Business Rules

### Scaling Logic
- **Piece products**: All ingredients multiplied by scale factor
- **Gram products**: All ingredients scaled proportionally
- **Mixed units**: Each ingredient scaled according to its unit type

### Precision Rules
- **Pieces**: Whole numbers for quantities ≥ 1, one decimal place for < 1
- **Grams**: Configurable decimal places (default: 3)
- **Rounding**: Uses ROUND_HALF_UP for consistent results

### Validation
- Scale factors must be between 0.001 and 1000
- Target quantities must be positive
- Units must match for scaling (piece-to-piece, gram-to-gram)
- Maximum 1000 ingredients per calculation

## Performance

### Response Times
- Standard calculations: < 100ms
- Hierarchical expansions: < 500ms
- Batch operations: < 2s for 50 calculations
- Cache hits: < 10ms

### Caching Strategy
- Redis-based result caching with configurable TTL
- Cache keys based on calculation parameters
- Automatic cache invalidation on recipe changes
- Cache statistics and monitoring

### Optimization Features
- Parallel batch processing
- Minimal memory footprint
- Efficient Redis operations
- Structured logging for monitoring

## Error Handling

The service provides detailed error responses:

- `400 Bad Request`: Invalid calculation parameters
- `404 Not Found`: Recipe not found
- `500 Internal Server Error`: Calculation failures
- `503 Service Unavailable`: External service failures

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (required)
redis-server

# Run development server
flask run --host=0.0.0.0 --port=8003
```

### Testing
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run performance tests
python -m pytest tests/performance/
```

### Docker Development
```bash
# Build image
docker build -t calculator-service .

# Run container
docker run -p 8003:8003 -e REDIS_URL=redis://host.docker.internal:6379/2 calculator-service
```

## Dependencies

### External Services
- **Recipe Service**: Recipe data and hierarchical relationships
- **Redis**: Caching layer for performance optimization

### Service Communication
- HTTP client with automatic retries and circuit breaker
- Structured logging for request/response tracking
- Health checks for dependency monitoring

## Monitoring

### Health Checks
- `/health`: Comprehensive health with dependency status
- `/api/v1/health/ready`: Kubernetes readiness probe
- `/api/v1/health/live`: Kubernetes liveness probe

### Metrics
- Calculation response times
- Cache hit/miss rates
- Error rates by type
- Memory usage statistics

### Logging
- Structured JSON logging
- Request/response tracking
- Performance metrics
- Error context and stack traces

## Security

- Input validation and sanitization
- Rate limiting on calculation endpoints
- Error message sanitization
- Container security best practices
- No sensitive data in logs

## Production Deployment

### Container Configuration
```yaml
calculator-service:
  image: calculator-service:latest
  ports:
    - "8003:8003"
  environment:
    - FLASK_ENV=production
    - REDIS_URL=redis://redis:6379/2
    - RECIPE_SERVICE_URL=http://recipe-service:8002
  depends_on:
    - redis
    - recipe-service
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Scaling Considerations
- Stateless service design for horizontal scaling
- Redis cluster support for high availability
- Load balancing across multiple instances
- CPU-optimized instances for calculation workloads