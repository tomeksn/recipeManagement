"""Health check resource for the Product Service."""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from sqlalchemy import text
from ..extensions import db

blp = Blueprint('health', __name__, description='Health check operations')


@blp.route('/health')
class HealthCheck(MethodView):
    """Health check endpoint."""
    
    def get(self):
        """Check service health.
        
        Returns health status of the service including database connectivity.
        """
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            
            return {
                'status': 'healthy',
                'service': 'product-service',
                'database': 'connected'
            }, 200
        except Exception as e:
            return {
                'status': 'unhealthy',
                'service': 'product-service',
                'database': 'disconnected',
                'error': str(e)
            }, 503