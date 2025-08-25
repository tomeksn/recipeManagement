"""API Gateway Flask Application Factory."""
import logging
import time
import uuid
import structlog
import redis
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_session import Session
from flask_smorest import Api

from .config import get_config
from .extensions import cache, session, limiter, talisman, init_redis_pool
from .resources import health
from .resources.proxy_simple import proxy_bp
from .utils.exceptions import register_error_handlers


def create_app(config_name: str = None) -> Flask:
    """Create Flask application with factory pattern.
    
    Args:
        config_name: Configuration name to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Override config if specified
    if config_name:
        app.config.from_object(f'app.config.{config_name}')
    
    # Setup structured logging
    configure_logging(app)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add middleware
    add_middleware(app)
    
    return app


def initialize_extensions(app: Flask) -> None:
    """Initialize Flask extensions.
    
    Args:
        app: Flask application instance
    """
    # Redis connection pool
    init_redis_pool(app.config['REDIS_URL'])
    
    # Cache
    cache.init_app(app, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': app.config['REDIS_URL'],
        'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_TTL']
    })
    
    # Session management
    app.config['SESSION_REDIS'] = redis.from_url(app.config['REDIS_URL'])
    session.init_app(app)
    
    # Rate limiting
    limiter.init_app(app)
    
    # CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         methods=app.config['CORS_METHODS'],
         allow_headers=app.config['CORS_HEADERS'],
         supports_credentials=True)
    
    # Security headers
    if app.config.get('FORCE_HTTPS'):
        talisman.init_app(app,
                         force_https=True,
                         content_security_policy=app.config['CONTENT_SECURITY_POLICY'])
    
    # API Documentation
    api = Api(app)
    
    # Configure API documentation
    api.spec.info = {
        'title': app.config['API_TITLE'],
        'version': app.config['API_VERSION'],
        'description': '''
# Recipe Management API Gateway

The API Gateway provides a unified entry point for all Recipe Management System APIs.
It handles request routing, authentication, rate limiting, caching, and service aggregation.

## Features

- **Unified API**: Single endpoint for all microservices
- **Request Routing**: Intelligent routing to appropriate backend services
- **Rate Limiting**: Protection against abuse and overload
- **Caching**: Performance optimization with Redis caching
- **Circuit Breaker**: Resilience against service failures
- **Health Monitoring**: Comprehensive health checks for all services
- **Security**: CORS, security headers, and authentication middleware

## Services

The gateway routes requests to the following backend services:

### Product Service
- **Base Path**: `/api/v1/products`
- **Description**: Product CRUD operations and search functionality
- **Health**: Monitored via `/health` endpoint

### Recipe Service  
- **Base Path**: `/api/v1/recipes`
- **Description**: Recipe management and hierarchical relationships
- **Health**: Monitored via `/health` endpoint

### Calculator Service
- **Base Path**: `/api/v1/calculations`
- **Description**: Recipe scaling calculations and ingredient conversion
- **Health**: Monitored via `/health` endpoint

## Authentication

The gateway supports JWT-based authentication:

```http
Authorization: Bearer <jwt-token>
```

## Rate Limiting

Default rate limits apply:
- **Default**: 1000 requests per hour per IP
- **Authenticated**: Higher limits for authenticated users
- **Headers**: Rate limit information in response headers

## Caching

GET requests are cached for performance:
- **Default TTL**: 5 minutes
- **Cache Keys**: Based on endpoint, parameters, and user context
- **Cache Headers**: `X-Cache-Status` indicates hit/miss

## Error Handling

Standardized error responses:

```json
{
  "error": "Error description",
  "status_code": 400,
  "timestamp": "2023-01-01T00:00:00Z",
  "service": "api-gateway",
  "details": {}
}
```

## Health Monitoring

- **Gateway Health**: `/health` - Overall system health
- **Readiness**: `/health/ready` - Kubernetes readiness probe
- **Liveness**: `/health/live` - Kubernetes liveness probe
- **Service Health**: `/health/services` - Individual service status
''',
        'contact': {
            'name': 'Recipe Management Team',
            'email': 'support@recipemanagement.com'
        }
    }
    
    api.spec.servers = [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
        {'url': '/api/v1', 'description': 'Production API'}
    ]
    
    # Add security scheme for JWT
    api.spec.components.security_scheme('BearerAuth', {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'JWT'
    })
    
    # Register API blueprints
    api.register_blueprint(health.blp)


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    # Register simple proxy blueprint
    app.register_blueprint(proxy_bp)
    # Root health check (also available outside API)
    @app.route('/health')
    def health_check():
        """Root health check endpoint for load balancers."""
        try:
            from .services.service_client import service_client
            
            # Quick health check of critical services
            critical_services = ['product', 'recipe']
            healthy_services = 0
            
            for service_name in critical_services:
                if service_client.health_check(service_name):
                    healthy_services += 1
            
            if healthy_services == len(critical_services):
                status = 'healthy'
                status_code = 200
            elif healthy_services > 0:
                status = 'degraded'
                status_code = 200
            else:
                status = 'unhealthy' 
                status_code = 503
            
            return jsonify({
                'status': status,
                'service': 'api-gateway',
                'version': app.config['API_VERSION'],
                'healthy_services': f"{healthy_services}/{len(critical_services)}"
            }), status_code
            
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'service': 'api-gateway',
                'error': str(e)
            }), 503
    
    # API documentation endpoint
    @app.route('/docs')
    def api_docs():
        """Redirect to API documentation."""
        return app.redirect('/swagger-ui')
    
    # Gateway information endpoint
    @app.route('/info')
    def gateway_info():
        """Get gateway configuration and status information."""
        return jsonify({
            'service': 'api-gateway',
            'version': app.config['API_VERSION'],
            'services': {
                name: {
                    'url': config['url'],
                    'prefix': config['prefix']
                }
                for name, config in app.config['SERVICES'].items()
            },
            'features': {
                'rate_limiting': hasattr(app, 'limiter'),
                'caching': hasattr(app, 'cache'),
                'security_headers': app.config.get('FORCE_HTTPS', False),
                'cors_enabled': True
            }
        })


def configure_logging(app: Flask) -> None:
    """Configure structured logging.
    
    Args:
        app: Flask application instance
    """
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            app.config['LOG_LEVEL']
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set Flask logger level
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    # Configure werkzeug logger
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def add_middleware(app: Flask) -> None:
    """Add middleware for request/response processing.
    
    Args:
        app: Flask application instance
    """
    logger = structlog.get_logger("api_gateway")
    
    @app.before_request
    def before_request():
        """Process requests before routing."""
        # Generate request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.request_id = request_id
        g.start_time = time.time()
        
        # Store request time for error handlers
        app.extensions['current_request_time'] = time.time()
        
        # Log incoming request
        logger.info(
            "Request received",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_id=request_id,
            content_length=request.content_length
        )
    
    @app.after_request
    def after_request(response):
        """Process responses after routing."""
        duration = (time.time() - g.get('start_time', time.time())) * 1000
        
        # Add gateway headers
        response.headers['X-Gateway-Version'] = app.config['API_VERSION']
        response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
        response.headers['X-Response-Time'] = f"{duration:.2f}ms"
        
        # Log outgoing response
        logger.info(
            "Request completed",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            content_length=response.content_length,
            duration_ms=round(duration, 2),
            request_id=g.get('request_id', 'unknown')
        )
        
        return response
    
    @app.teardown_appcontext
    def teardown(error=None):
        """Clean up after request."""
        if error:
            logger.error(
                "Request teardown with error",
                error=str(error),
                request_id=g.get('request_id', 'unknown')
            )