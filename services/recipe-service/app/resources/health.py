"""Health check resource for the Recipe Service."""
from flask.views import MethodView
from flask_smorest import Blueprint
from flask import jsonify
from sqlalchemy import text

from ..extensions import db
from ..services.product_client import get_product_client

blp = Blueprint('health', __name__, description='Health check operations')


@blp.route('/health')
class HealthCheck(MethodView):
    """Health check endpoint."""
    
    def get(self):
        """Check service health.
        
        Returns health status of the service including database connectivity
        and external service dependencies.
        """
        health_status = {
            'status': 'healthy',
            'service': 'recipe-service',
            'dependencies': {}
        }
        
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            health_status['dependencies']['database'] = 'connected'
        except Exception as e:
            health_status['dependencies']['database'] = f'disconnected: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Test Product Service connection
        try:
            client = get_product_client()
            product_service_healthy = client.health_check()
            health_status['dependencies']['product_service'] = 'connected' if product_service_healthy else 'disconnected'
            
            if not product_service_healthy:
                health_status['status'] = 'degraded'  # Can function but with limited capability
        except Exception as e:
            health_status['dependencies']['product_service'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'
        
        # Determine overall status
        if health_status['status'] == 'healthy':
            return health_status, 200
        elif health_status['status'] == 'degraded':
            return health_status, 200  # Still functional
        else:
            return health_status, 503  # Service unavailable