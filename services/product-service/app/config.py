"""Configuration settings for the Product Service."""
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
            'options': '-csearch_path=product_service,public'
        }
    }
    
    # Redis Cache
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
    REDIS_DB = int(os.environ.get('REDIS_DB', '0'))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # API Configuration
    API_TITLE = 'Product Service API'
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
    
    # Search Cache
    SEARCH_CACHE_TTL = 300  # 5 minutes
    SEARCH_CACHE_MAX_ENTRIES = 1000
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    LOG_LEVEL = 'DEBUG'


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


def get_config() -> Type[Config]:
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    return config_map.get(env, DevelopmentConfig)