"""Configuration settings for Calculator Service."""
import os
import logging
from typing import Type


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-calculator-secret-key'
    
    # API settings
    API_VERSION = 'v1.0.0'
    
    # Redis settings
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
    REDIS_URL = os.environ.get('REDIS_URL') or f'redis://{REDIS_HOST}:{REDIS_PORT}/2'
    CACHE_TTL = int(os.environ.get('CACHE_TTL', 3600))  # 1 hour default
    
    # External services
    RECIPE_SERVICE_URL = os.environ.get('RECIPE_SERVICE_URL') or 'http://localhost:8002'
    RECIPE_SERVICE_TIMEOUT = int(os.environ.get('RECIPE_SERVICE_TIMEOUT', 30))
    RECIPE_SERVICE_RETRIES = int(os.environ.get('RECIPE_SERVICE_RETRIES', 3))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # API settings
    API_TITLE = 'Recipe Management Calculator Service API'
    API_VERSION = 'v1.0.0'
    OPENAPI_VERSION = '3.0.2'
    
    # Logging
    LOG_LEVEL = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
    
    # Calculation settings
    PRECISION_DECIMAL_PLACES = int(os.environ.get('PRECISION_DECIMAL_PLACES', 3))
    MAX_SCALE_FACTOR = float(os.environ.get('MAX_SCALE_FACTOR', 1000.0))
    MIN_SCALE_FACTOR = float(os.environ.get('MIN_SCALE_FACTOR', 0.001))
    MAX_INGREDIENTS_PER_CALCULATION = int(os.environ.get('MAX_INGREDIENTS_PER_CALCULATION', 1000))
    
    # Performance settings
    CALCULATION_CACHE_TTL = int(os.environ.get('CALCULATION_CACHE_TTL', 1800))  # 30 minutes
    ENABLE_RESULT_CACHING = os.environ.get('ENABLE_RESULT_CACHING', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    LOG_LEVEL = logging.DEBUG
    
    # Relaxed cache settings for development
    CACHE_TTL = 300  # 5 minutes
    CALCULATION_CACHE_TTL = 60  # 1 minute


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    
    # Use different Redis DB for testing
    REDIS_URL = os.environ.get('REDIS_TEST_URL') or f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/12'
    
    # Disable caching in tests by default
    CACHE_TTL = 0
    CALCULATION_CACHE_TTL = 0
    ENABLE_RESULT_CACHING = False
    
    # Fast timeouts for testing
    RECIPE_SERVICE_TIMEOUT = 5
    RECIPE_SERVICE_RETRIES = 1


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    LOG_LEVEL = logging.INFO
    
    # Production cache settings
    CACHE_TTL = 7200  # 2 hours
    CALCULATION_CACHE_TTL = 3600  # 1 hour
    
    # Production performance settings
    RECIPE_SERVICE_TIMEOUT = 30
    RECIPE_SERVICE_RETRIES = 3


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