"""Flask extensions initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
cache = Cache()
migrate = Migrate()