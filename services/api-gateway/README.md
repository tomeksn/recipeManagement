# API Gateway

Centralized API Gateway for the Recipe Management System. Provides unified access to all microservices with request routing, rate limiting, caching, authentication, and comprehensive monitoring.

## Features

- **Unified API**: Single entry point for all microservices
- **Intelligent Routing**: Request routing to appropriate backend services
- **Rate Limiting**: Protection against abuse and overload
- **Caching**: Redis-based performance optimization
- **Circuit Breaker**: Resilience against service failures
- **Health Monitoring**: Comprehensive health checks for all services
- **Security**: CORS, security headers, JWT authentication
- **Observability**: Structured logging and request tracing

## Architecture

### Service Routing

The gateway routes requests based on URL patterns:

- `/api/v1/products/*` → Product Service (port 8001)
- `/api/v1/recipes/*` → Recipe Service (port 8002)  
- `/api/v1/calculations/*` → Calculator Service (port 8003)

### Request Flow

```
Client → API Gateway → Backend Service → Database
  ↓         ↓              ↓
Cache ← Logging ←    Response
```

## API Endpoints

### Health Monitoring

```http
GET /health                 # Quick health check
GET /health/                # Detailed health with dependencies
GET /health/ready           # Kubernetes readiness probe
GET /health/live            # Kubernetes liveness probe
GET /health/services        # Individual service health
```

### Service Proxying

All backend service endpoints are available through the gateway:

#### Product Management
```http
GET    /api/v1/products           # List products
POST   /api/v1/products           # Create product
GET    /api/v1/products/{id}      # Get product
PUT    /api/v1/products/{id}      # Update product
DELETE /api/v1/products/{id}      # Delete product
GET    /api/v1/products/search    # Search products
```

#### Recipe Management
```http
GET    /api/v1/recipes                    # List recipes
POST   /api/v1/recipes                    # Create recipe
GET    /api/v1/recipes/{id}               # Get recipe
PUT    /api/v1/recipes/{id}               # Update recipe
DELETE /api/v1/recipes/{id}               # Delete recipe
GET    /api/v1/recipes/product/{id}       # Get recipe by product
GET    /api/v1/recipes/product/{id}/hierarchy  # Get recipe hierarchy
```

#### Recipe Calculations
```http
POST   /api/v1/calculations/calculate     # Calculate recipe
POST   /api/v1/calculations/calculate/batch  # Batch calculations
GET    /api/v1/calculations/history       # Calculation history
GET    /api/v1/calculations/cache/stats   # Cache statistics
POST   /api/v1/calculations/cache/clear   # Clear cache
```

### Gateway Information

```http
GET /info                   # Gateway configuration and status
GET /docs                   # API documentation (Swagger UI)
```

## Configuration

Environment variables for configuration:

```bash
# Service Configuration
FLASK_ENV=development
PORT=8000
SECRET_KEY=your-secret-key

# Backend Services
PRODUCT_SERVICE_URL=http://localhost:8001
RECIPE_SERVICE_URL=http://localhost:8002
CALCULATOR_SERVICE_URL=http://localhost:8003

# Service Communication
SERVICE_TIMEOUT=30
SERVICE_RETRIES=3
SERVICE_BACKOFF_FACTOR=0.3

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# Rate Limiting
RATELIMIT_DEFAULT=1000 per hour

# Security
JWT_SECRET_KEY=your-jwt-secret
FORCE_HTTPS=false
CORS_ORIGINS=http://localhost:3000

# Circuit Breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60

# Request Processing
MAX_CONTENT_LENGTH=16777216  # 16MB
REQUEST_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
```

## Request Headers

### Standard Headers
- `Authorization: Bearer <token>` - JWT authentication
- `Content-Type: application/json` - Request content type
- `Accept: application/json` - Response content type

### Gateway Headers (added automatically)
- `X-Forwarded-By: recipe-management-gateway` - Gateway identification
- `X-Forwarded-For: <client-ip>` - Original client IP
- `X-Original-Path: <path>` - Original request path
- `X-Request-ID: <uuid>` - Unique request identifier

### Response Headers (added by gateway)
- `X-Gateway-Version: <version>` - Gateway version
- `X-Request-ID: <uuid>` - Request correlation ID
- `X-Response-Time: <time>ms` - Total processing time
- `X-Cache-Status: hit/miss` - Cache status (for cached responses)

## Rate Limiting

### Default Limits
- **Unauthenticated**: 1000 requests per hour per IP
- **Authenticated**: Higher limits based on user tier
- **Admin**: Unlimited (configurable)

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
Retry-After: 3600
```

## Caching

### Cache Strategy
- **GET requests only**: Only read operations are cached
- **TTL**: 5 minutes default (configurable)
- **Cache Keys**: Based on endpoint, parameters, and user context
- **Invalidation**: Automatic on POST/PUT/DELETE to same resource

### Cache Headers
```http
X-Cache-Status: hit        # Response served from cache
X-Cache-Status: miss       # Response fetched from service
```

## Error Handling

### Standard Error Response
```json
{
  "error": "Error description",
  "status_code": 400,
  "timestamp": "2023-01-01T00:00:00Z",
  "service": "api-gateway",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "details": {}
}
```

### Error Types
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Gateway error
- `502 Bad Gateway` - Invalid response from backend
- `503 Service Unavailable` - Backend service down
- `504 Gateway Timeout` - Backend service timeout

## Circuit Breaker

### States
- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Service failing, requests rejected immediately
- **HALF_OPEN**: Testing if service has recovered

### Configuration
- **Failure Threshold**: 5 consecutive failures (configurable)
- **Recovery Timeout**: 60 seconds (configurable)
- **Success Threshold**: 1 success to close circuit

## Security

### Features
- **CORS**: Configurable cross-origin resource sharing
- **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- **Rate Limiting**: Protection against abuse
- **Request Validation**: Size limits and input validation
- **JWT Authentication**: Token-based authentication
- **Input Sanitization**: Protection against injection attacks

### Security Headers
```http
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (required)
redis-server

# Run development server
flask run --host=0.0.0.0 --port=8000
```

### Testing
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_health.py
```

### Docker Development
```bash
# Build image
docker build -t api-gateway .

# Run container
docker run -p 8000:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e PRODUCT_SERVICE_URL=http://host.docker.internal:8001 \
  -e RECIPE_SERVICE_URL=http://host.docker.internal:8002 \
  -e CALCULATOR_SERVICE_URL=http://host.docker.internal:8003 \
  api-gateway
```

## Monitoring

### Health Checks
- **Load Balancer**: `/health` - Quick status for load balancers
- **Detailed**: `/health/` - Comprehensive health with dependencies
- **Kubernetes**: `/health/ready` and `/health/live` - K8s probes

### Metrics
- Request rate and response times
- Error rates by service and endpoint
- Cache hit/miss ratios
- Circuit breaker state changes
- Service availability percentages

### Logging
```json
{
  "timestamp": "2023-01-01T00:00:00Z",
  "level": "INFO",
  "service": "api-gateway",
  "message": "Request completed",
  "method": "GET",
  "path": "/api/v1/products",
  "status_code": 200,
  "duration_ms": 45.2,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Performance

### Benchmarks
- **Response Time**: < 50ms for cached responses
- **Throughput**: 1000+ requests/second (4 workers)
- **Memory Usage**: < 100MB per worker
- **Cache Hit Rate**: 60-80% for read operations

### Optimization
- Connection pooling for backend services
- Redis pipeline for batch operations
- HTTP/2 support for client connections
- Compression for large responses

## Production Deployment

### Container Configuration
```yaml
api-gateway:
  image: api-gateway:latest
  ports:
    - "8000:8000"
  environment:
    - FLASK_ENV=production
    - REDIS_URL=redis://redis:6379/0
    - PRODUCT_SERVICE_URL=http://product-service:8001
    - RECIPE_SERVICE_URL=http://recipe-service:8002
    - CALCULATOR_SERVICE_URL=http://calculator-service:8003
  depends_on:
    - redis
    - product-service
    - recipe-service
    - calculator-service
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Load Balancing
- Multiple gateway instances behind load balancer
- Session affinity not required (stateless design)
- Health check integration for automatic failover

### Scaling Considerations
- Horizontal scaling with Redis cluster
- CPU-optimized instances for request processing
- Network optimization for service communication
- CDN integration for static content