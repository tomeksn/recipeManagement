"""Health check resources for Calculator Service."""
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields

from ..extensions import cache

blp = Blueprint(
    'health',
    __name__,
    url_prefix='/api/v1/health',
    description='Health check endpoints'
)


class HealthSchema(Schema):
    """Health check response schema."""
    status = fields.Str(required=True, description="Service health status")
    service = fields.Str(required=True, description="Service name")
    version = fields.Str(required=True, description="API version")
    dependencies = fields.Dict(description="Dependency health status")
    performance = fields.Dict(description="Performance metrics")


@blp.route('/')
class HealthCheck(MethodView):
    """Health check endpoint."""
    
    @blp.response(200, HealthSchema)
    def get(self):
        """Get service health status.
        
        Returns comprehensive health information including dependencies
        and performance metrics for monitoring systems.
        """
        try:
            # Test Redis connection
            cache_key = 'health_check_test'
            cache.set(cache_key, 'ok', timeout=10)
            cache_healthy = cache.get(cache_key) == 'ok'
            cache.delete(cache_key)
            
            # Test Recipe Service connection
            from ..services.recipe_client import get_recipe_client
            recipe_service_healthy = True
            recipe_service_latency = None
            
            try:
                import time
                start_time = time.time()
                recipe_service_healthy = get_recipe_client().health_check()
                recipe_service_latency = round((time.time() - start_time) * 1000, 2)
            except Exception as e:
                current_app.logger.warning(f"Recipe service health check failed: {str(e)}")
                recipe_service_healthy = False
            
            # Determine overall status
            overall_healthy = cache_healthy and recipe_service_healthy
            status = 'healthy' if overall_healthy else 'degraded'
            
            return {
                'status': status,
                'service': 'calculator-service',
                'version': current_app.config['API_VERSION'],
                'dependencies': {
                    'redis': 'connected' if cache_healthy else 'disconnected',
                    'recipe_service': 'connected' if recipe_service_healthy else 'disconnected'
                },
                'performance': {
                    'recipe_service_latency_ms': recipe_service_latency
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'service': 'calculator-service',
                'version': current_app.config.get('API_VERSION', 'unknown'),
                'error': str(e)
            }, 503


@blp.route('/ready')
class ReadinessCheck(MethodView):
    """Readiness check endpoint for Kubernetes."""
    
    @blp.response(200, HealthSchema)
    def get(self):
        """Check if service is ready to accept requests."""
        try:
            # Quick Redis connection test
            cache.get('readiness_check')
            
            return {
                'status': 'ready',
                'service': 'calculator-service',
                'version': current_app.config['API_VERSION'],
                'dependencies': {
                    'redis': 'connected'
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Readiness check failed: {str(e)}")
            return {
                'status': 'not_ready',
                'service': 'calculator-service',
                'error': str(e)
            }, 503


@blp.route('/live')
class LivenessCheck(MethodView):
    """Liveness check endpoint for Kubernetes."""
    
    @blp.response(200, HealthSchema)
    def get(self):
        """Check if service is alive and responding."""
        return {
            'status': 'alive',
            'service': 'calculator-service',
            'version': current_app.config['API_VERSION']
        }