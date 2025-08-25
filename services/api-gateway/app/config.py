"""Configuration settings for API Gateway."""
import os
import logging
from typing import Type, Dict, Any


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-gateway-secret-key'
    
    # API settings
    API_VERSION = 'v1.0.0'
    API_TITLE = 'Recipe Management API Gateway'
    OPENAPI_VERSION = '3.0.2'
    
    # Service URLs
    PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL') or 'http://recipe_product_service:8001'
    RECIPE_SERVICE_URL = os.environ.get('RECIPE_SERVICE_URL') or 'http://recipe_recipe_service:8002'
    CALCULATOR_SERVICE_URL = os.environ.get('CALCULATOR_SERVICE_URL') or 'http://recipe_calculator_service:8003'
    
    # Service timeouts and retries
    SERVICE_TIMEOUT = int(os.environ.get('SERVICE_TIMEOUT', 30))
    SERVICE_RETRIES = int(os.environ.get('SERVICE_RETRIES', 3))
    SERVICE_BACKOFF_FACTOR = float(os.environ.get('SERVICE_BACKOFF_FACTOR', 0.3))
    
    # Redis settings for caching and sessions
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://recipe_redis:6379/0'
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Set in app initialization
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'gateway:'
    
    # Cache settings
    CACHE_TTL = int(os.environ.get('CACHE_TTL', 300))  # 5 minutes default
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://172.27.214.48:3000').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With', 'X-Request-ID', 'X-Correlation-ID', 'Accept', 'Accept-Language', 'User-Agent']
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'redis://recipe_redis:6379/1'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '1000 per hour')
    RATELIMIT_HEADERS_ENABLED = True
    
    # Authentication & Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days
    
    # Security headers
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'false').lower() == 'true'
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'connect-src': "'self'",
        'font-src': "'self'",
        'object-src': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'"
    }
    
    # Logging
    LOG_LEVEL = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
    
    # Service discovery
    CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
    CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
    SERVICE_DISCOVERY_ENABLED = os.environ.get('SERVICE_DISCOVERY_ENABLED', 'false').lower() == 'true'
    
    # Load balancing
    LOAD_BALANCING_STRATEGY = os.environ.get('LOAD_BALANCING_STRATEGY', 'round_robin')  # round_robin, random, weighted
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 60))
    
    # Request/Response settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 30))
    
    # Service configuration
    SERVICES = {
        'product': {
            'name': 'product-service',
            'url': PRODUCT_SERVICE_URL,
            'prefix': '/api/v1/products',
            'health_endpoint': '/health',
            'timeout': SERVICE_TIMEOUT,
            'retries': SERVICE_RETRIES
        },
        'recipe': {
            'name': 'recipe-service', 
            'url': RECIPE_SERVICE_URL,
            'prefix': '/api/v1/recipes',
            'health_endpoint': '/health',
            'timeout': SERVICE_TIMEOUT,
            'retries': SERVICE_RETRIES
        },
        'calculator': {
            'name': 'calculator-service',
            'url': CALCULATOR_SERVICE_URL,
            'prefix': '/api/v1/calculations',
            'health_endpoint': '/health',
            'timeout': SERVICE_TIMEOUT,
            'retries': SERVICE_RETRIES
        }
    }
    
    @classmethod
    def get_service_config(cls, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service configuration dictionary
        """
        return cls.SERVICES.get(service_name, {})


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    LOG_LEVEL = logging.DEBUG
    
    # Relaxed settings for development
    CACHE_TTL = 60  # 1 minute
    RATELIMIT_DEFAULT = '10000 per hour'  # More lenient
    FORCE_HTTPS = False
    
    # Development service URLs
    SERVICES = {
        **Config.SERVICES,
        'product': {**Config.SERVICES['product'], 'url': 'http://recipe_product_service:8001'},
        'recipe': {**Config.SERVICES['recipe'], 'url': 'http://recipe_recipe_service:8002'},
        'calculator': {**Config.SERVICES['calculator'], 'url': 'http://recipe_calculator_service:8003'}
    }


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    
    # Use different Redis DBs for testing
    REDIS_URL = os.environ.get('REDIS_TEST_URL') or 'redis://localhost:6379/10'
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379/11'
    
    # Disable some features in testing
    RATELIMIT_ENABLED = False
    CACHE_TTL = 0
    
    # Fast timeouts for testing
    SERVICE_TIMEOUT = 5
    SERVICE_RETRIES = 1
    
    # Mock service URLs for testing
    SERVICES = {
        'product': {
            'name': 'product-service',
            'url': 'http://mock-product-service:8001',
            'prefix': '/api/v1/products',
            'health_endpoint': '/health',
            'timeout': 5,
            'retries': 1
        },
        'recipe': {
            'name': 'recipe-service',
            'url': 'http://mock-recipe-service:8002', 
            'prefix': '/api/v1/recipes',
            'health_endpoint': '/health',
            'timeout': 5,
            'retries': 1
        },
        'calculator': {
            'name': 'calculator-service',
            'url': 'http://mock-calculator-service:8003',
            'prefix': '/api/v1/calculations',
            'health_endpoint': '/health',
            'timeout': 5,
            'retries': 1
        }
    }


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    LOG_LEVEL = logging.INFO
    
    # Production security settings
    FORCE_HTTPS = True
    
    # Production cache settings
    CACHE_TTL = 300  # 5 minutes
    
    # Production rate limiting
    RATELIMIT_DEFAULT = '1000 per hour'
    
    # Enable service discovery in production
    SERVICE_DISCOVERY_ENABLED = True
    
    # Production service URLs (from environment or service discovery)
    SERVICES = {
        'product': {
            'name': 'product-service',
            'url': os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8001'),
            'prefix': '/api/v1/products',
            'health_endpoint': '/health',
            'timeout': Config.SERVICE_TIMEOUT,
            'retries': Config.SERVICE_RETRIES
        },
        'recipe': {
            'name': 'recipe-service',
            'url': os.environ.get('RECIPE_SERVICE_URL', 'http://recipe-service:8002'),
            'prefix': '/api/v1/recipes', 
            'health_endpoint': '/health',
            'timeout': Config.SERVICE_TIMEOUT,
            'retries': Config.SERVICE_RETRIES
        },
        'calculator': {
            'name': 'calculator-service',
            'url': os.environ.get('CALCULATOR_SERVICE_URL', 'http://calculator-service:8003'),
            'prefix': '/api/v1/calculations',
            'health_endpoint': '/health',
            'timeout': Config.SERVICE_TIMEOUT,
            'retries': Config.SERVICE_RETRIES
        }
    }


def get_config() -> Type[Config]:
    """Get configuration class based on environment.
    
    Returns:
        Configuration class to use
    """
    config_name = os.environ.get('FLASK_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'prod': ProductionConfig
    }
    
    return config_map.get(config_name, DevelopmentConfig)