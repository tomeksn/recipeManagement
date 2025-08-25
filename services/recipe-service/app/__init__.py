"""Recipe Service Flask Application Factory."""
import logging
import structlog
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_smorest import Api

from .config import get_config
from .extensions import db, cache
from .resources import health, recipes
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
    # Database
    db.init_app(app)
    
    # Migrations
    Migrate(app, db)
    
    # Cache
    cache.init_app(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': app.config['REDIS_URL']})
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # API Documentation
    api = Api(app)
    
    # Configure API documentation
    api.spec.info = {
        'title': 'Recipe Management Recipe Service API',
        'version': 'v1.0.0',
        'description': '''
# Recipe Service API

The Recipe Service manages recipes and their ingredients in the Recipe Management System.
It provides comprehensive recipe management capabilities including CRUD operations, 
hierarchical recipe expansion, and circular dependency prevention.

## Features

- **Recipe Management**: Create, read, update, and delete recipes
- **Ingredient Management**: Add, modify, and remove ingredients from recipes
- **Hierarchical Recipes**: Support for nested recipes with semi-products
- **Circular Dependency Prevention**: Automatic detection and prevention of recipe loops
- **Product Integration**: Seamless integration with Product Service
- **Audit Trail**: Complete change history tracking

## Recipe Types

Recipes can contain different types of ingredients:
- **Standard Products**: Basic ingredients measured in pieces or grams
- **Semi Products**: Products that have their own recipes (hierarchical)
- **Kit Products**: Collections of products used as single ingredients

## Business Rules

- Each product can have only one recipe
- Recipes must have at least one ingredient
- Circular dependencies are not allowed in recipe hierarchies
- Ingredient quantities must be positive numbers
- Recipe depth is limited to prevent performance issues
''',
        'contact': {
            'name': 'Recipe Management Team',
            'email': 'support@recipemanagement.com'
        }
    }
    
    api.spec.servers = [
        {'url': 'http://localhost:8002', 'description': 'Development server'},
        {'url': '/api/v1', 'description': 'Production API'}
    ]
    
    # Register API blueprints with smorest
    api.register_blueprint(health.blp)
    api.register_blueprint(recipes.blp)


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
            # Test database connection
            db.session.execute('SELECT 1')
            
            # Test Product Service connection (optional for basic health)
            from .services.product_client import get_product_client
            product_service_healthy = True
            try:
                product_service_healthy = get_product_client().health_check()
            except Exception:
                product_service_healthy = False
            
            return jsonify({
                'status': 'healthy' if product_service_healthy else 'degraded',
                'service': 'recipe-service',
                'version': app.config['API_VERSION'],
                'dependencies': {
                    'database': 'connected',
                    'product_service': 'connected' if product_service_healthy else 'disconnected'
                }
            }), 200
            
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'service': 'recipe-service',
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
            logging.getLevelName(app.config['LOG_LEVEL'])
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
    logger = structlog.get_logger("recipe_service")
    
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