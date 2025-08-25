"""Flask extensions for API Gateway."""
from flask_caching import Cache
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import redis

# Initialize extensions
cache = Cache()
session = Session()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()

# Redis connection pool for shared use
redis_pool = None


def init_redis_pool(redis_url: str):
    """Initialize Redis connection pool.
    
    Args:
        redis_url: Redis connection URL
    """
    global redis_pool
    redis_pool = redis.ConnectionPool.from_url(redis_url)


def get_redis_connection():
    """Get Redis connection from pool.
    
    Returns:
        Redis connection instance
    """
    if redis_pool:
        return redis.Redis(connection_pool=redis_pool)
    return None