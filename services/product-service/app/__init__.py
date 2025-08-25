"""Product Service Flask Application Factory."""
import logging
import structlog
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_smorest import Api

from .config import get_config
from .extensions import db, cache
from .resources import products, health, search
from .utils.exceptions import register_error_handlers
from .docs.api_info import API_INFO


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
    api.spec.info = API_INFO
    api.spec.servers = [
        {'url': 'http://localhost:8001', 'description': 'Development server'},
        {'url': '/api/v1', 'description': 'Production API'}
    ]
    
    # Register API blueprints with smorest
    api.register_blueprint(products.blp)
    api.register_blueprint(health.blp)
    api.register_blueprint(search.blp)


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for container orchestration."""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'service': 'product-service',
                'version': app.config['API_VERSION']
            }), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'service': 'product-service',
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
    logger = structlog.get_logger("product_service")
    
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