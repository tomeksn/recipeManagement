"""Calculator Service Flask Application Factory.

Lightweight Flask application for recipe calculation operations.
Focuses on high-performance calculations with minimal overhead.
"""
import logging
import structlog
from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api

from .config import get_config
from .extensions import cache
from .resources import health, calculations
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
    
    # Add request logging
    add_request_logging(app)
    
    return app


def initialize_extensions(app: Flask) -> None:
    """Initialize Flask extensions.
    
    Args:
        app: Flask application instance
    """
    # Cache
    cache.init_app(app, config={
        'CACHE_TYPE': 'redis', 
        'CACHE_REDIS_URL': app.config['REDIS_URL'],
        'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_TTL']
    })
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # API Documentation
    api = Api(app)
    
    # Configure API documentation
    api.spec.info = {
        'title': 'Recipe Management Calculator Service API',
        'version': 'v1.0.0',
        'description': '''
# Calculator Service API

The Calculator Service provides high-performance recipe scaling calculations 
for the Recipe Management System. It handles quantity conversions, proportional 
scaling, and mixed-unit calculations with precision control.

## Features

- **Recipe Scaling**: Scale recipes to any target quantity or weight
- **Unit Handling**: Support for piece and gram measurements with mixed units
- **Precision Control**: Configurable rounding and decimal precision
- **Performance Optimization**: Redis caching for frequent calculations
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

## Performance

- Sub-100ms response times for standard calculations
- Redis caching with configurable TTL
- Optimized algorithms for large ingredient lists
- Minimal memory footprint
''',
        'contact': {
            'name': 'Recipe Management Team',
            'email': 'support@recipemanagement.com'
        }
    }
    
    api.spec.servers = [
        {'url': 'http://localhost:8003', 'description': 'Development server'},
        {'url': '/api/v1', 'description': 'Production API'}
    ]
    
    # Register API blueprints with smorest
    api.register_blueprint(health.blp)
    api.register_blueprint(calculations.blp)


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    # Health check endpoint (also available outside API)
    @app.route('/health')
    def health_check():
        """Health check endpoint for container orchestration."""
        try:
            # Test Redis connection
            cache.get('health_check')
            
            # Test Recipe Service connection
            from .services.recipe_client import get_recipe_client
            recipe_service_healthy = True
            try:
                recipe_service_healthy = get_recipe_client().health_check()
            except Exception:
                recipe_service_healthy = False
            
            return jsonify({
                'status': 'healthy' if recipe_service_healthy else 'degraded',
                'service': 'calculator-service',
                'version': app.config['API_VERSION'],
                'dependencies': {
                    'redis': 'connected',
                    'recipe_service': 'connected' if recipe_service_healthy else 'disconnected'
                }
            }), 200
            
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'service': 'calculator-service',
                'error': str(e)
            }), 503


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


def add_request_logging(app: Flask) -> None:
    """Add request/response logging middleware.
    
    Args:
        app: Flask application instance
    """
    logger = structlog.get_logger("calculator_service")
    
    @app.before_request
    def log_request():
        """Log incoming requests."""
        from flask import request
        logger.info(
            "Request received",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses."""
        from flask import request
        logger.info(
            "Request completed",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            content_length=response.content_length
        )
        return response