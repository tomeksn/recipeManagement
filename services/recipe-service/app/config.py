"""Configuration settings for the Recipe Service."""
import os
from typing import Type


class Config:
    """Base configuration class."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    DATABASE_PORT = os.environ.get('DATABASE_PORT', '5432')
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'recipe_management_dev')
    DATABASE_USER = os.environ.get('DATABASE_USER', 'recipe_user')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'recipe_password')
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@"
        f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {
            'options': '-csearch_path=recipe_service,public'
        }
    }
    
    # Redis Cache
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
    REDIS_DB = int(os.environ.get('REDIS_DB', '1'))  # Different DB than product service
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Service Communication
    PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:8001')
    SERVICE_TIMEOUT = int(os.environ.get('SERVICE_TIMEOUT', '30'))  # seconds
    
    # API Configuration
    API_TITLE = 'Recipe Service API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_URL_PREFIX = '/docs'
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_REDOC_URL = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Recipe Configuration
    MAX_RECIPE_DEPTH = int(os.environ.get('MAX_RECIPE_DEPTH', '10'))  # Maximum nesting depth
    MAX_INGREDIENTS_PER_RECIPE = int(os.environ.get('MAX_INGREDIENTS_PER_RECIPE', '100'))
    
    # Cache Configuration
    RECIPE_CACHE_TTL = 300  # 5 minutes
    HIERARCHY_CACHE_TTL = 600  # 10 minutes for hierarchical queries
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    LOG_LEVEL = 'DEBUG'
    
    # Relaxed limits for development
    MAX_RECIPE_DEPTH = 20
    MAX_INGREDIENTS_PER_RECIPE = 200


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable cache for testing
    CACHE_TYPE = 'null'
    
    # Mock external services
    PRODUCT_SERVICE_URL = 'http://mock-product-service'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Enhanced security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        'pool_size': 20,
        'max_overflow': 30,
    }
    
    # Stricter limits for production
    MAX_RECIPE_DEPTH = 15
    MAX_INGREDIENTS_PER_RECIPE = 150


def get_config() -> Type[Config]:
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    return config_map.get(env, DevelopmentConfig)