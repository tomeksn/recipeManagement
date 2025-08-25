"""Health check resources for API Gateway."""
import time
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint
from marshmallow import Schema, fields

from ..services.service_client import service_client

blp = Blueprint(
    'health',
    __name__,
    url_prefix='/health',
    description='Health check endpoints for API Gateway'
)


class HealthSchema(Schema):
    """Health check response schema."""
    status = fields.Str(required=True, description="Overall health status")
    service = fields.Str(required=True, description="Service name")
    version = fields.Str(required=True, description="API version")
    timestamp = fields.DateTime(required=True, description="Health check timestamp")
    dependencies = fields.Dict(description="Backend service health status")
    gateway_info = fields.Dict(description="Gateway-specific information")
    response_time_ms = fields.Float(description="Health check response time")


class ServiceHealthSchema(Schema):
    """Individual service health schema."""
    status = fields.Str(required=True, description="Service health status")
    response_time_ms = fields.Float(description="Service response time")
    last_check = fields.DateTime(description="Last health check timestamp")
    url = fields.Str(description="Service URL")


@blp.route('/')
class HealthCheck(MethodView):
    """Main health check endpoint."""
    
    @blp.response(200, HealthSchema)
    @blp.alt_response(503, description="Service unhealthy")
    def get(self):
        """Get comprehensive health status of API Gateway and all backend services.
        
        Returns detailed health information including:
        - Overall gateway status
        - Backend service availability
        - Response times and performance metrics
        - Configuration information
        """
        start_time = time.time()
        
        try:
            # Check all backend services
            service_health = {}
            overall_healthy = True
            
            for service_name, service_config in current_app.config['SERVICES'].items():
                service_start = time.time()
                is_healthy = service_client.health_check(service_name)
                service_time = (time.time() - service_start) * 1000
                
                service_health[service_name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'response_time_ms': round(service_time, 2),
                    'url': service_config['url']
                }
                
                if not is_healthy:
                    overall_healthy = False
            
            # Determine overall status
            if overall_healthy:
                status = 'healthy'
                status_code = 200
            else:
                status = 'degraded'
                status_code = 200  # Gateway is still functional
                
            # Calculate total response time
            total_time = (time.time() - start_time) * 1000
            
            response_data = {
                'status': status,
                'service': 'api-gateway',
                'version': current_app.config['API_VERSION'],
                'timestamp': time.time(),
                'dependencies': service_health,
                'gateway_info': {
                    'total_services': len(current_app.config['SERVICES']),
                    'healthy_services': sum(1 for s in service_health.values() if s['status'] == 'healthy'),
                    'cache_enabled': hasattr(current_app, 'cache'),
                    'rate_limiting_enabled': hasattr(current_app, 'limiter'),
                },
                'response_time_ms': round(total_time, 2)
            }
            
            return response_data, status_code
            
        except Exception as e:
            current_app.logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'service': 'api-gateway',
                'version': current_app.config.get('API_VERSION', 'unknown'),
                'timestamp': time.time(),
                'error': str(e),
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }, 503


@blp.route('/ready')
class ReadinessCheck(MethodView):
    """Readiness check endpoint for Kubernetes."""
    
    @blp.response(200, HealthSchema)
    @blp.alt_response(503, description="Service not ready")
    def get(self):
        """Check if API Gateway is ready to accept requests.
        
        Verifies that:
        - Flask application is properly initialized
        - Extensions are loaded
        - Critical backend services are available
        """
        try:
            # Check if essential services are available
            critical_services = ['product', 'recipe']  # Calculator is nice-to-have
            ready = True
            
            service_status = {}
            for service_name in critical_services:
                is_healthy = service_client.health_check(service_name)
                service_status[service_name] = 'ready' if is_healthy else 'not_ready'
                if not is_healthy:
                    ready = False
            
            status = 'ready' if ready else 'not_ready'
            status_code = 200 if ready else 503
            
            return {
                'status': status,
                'service': 'api-gateway',
                'version': current_app.config['API_VERSION'],
                'timestamp': time.time(),
                'dependencies': service_status
            }, status_code
            
        except Exception as e:
            current_app.logger.error(f"Readiness check failed: {str(e)}")
            return {
                'status': 'not_ready',
                'service': 'api-gateway',
                'error': str(e),
                'timestamp': time.time()
            }, 503


@blp.route('/live')
class LivenessCheck(MethodView):
    """Liveness check endpoint for Kubernetes."""
    
    @blp.response(200, HealthSchema)
    def get(self):
        """Check if API Gateway is alive and responding.
        
        Simple endpoint that verifies the application is running
        and can handle basic requests.
        """
        return {
            'status': 'alive',
            'service': 'api-gateway',
            'version': current_app.config['API_VERSION'],
            'timestamp': time.time()
        }


@blp.route('/services')
class ServicesHealth(MethodView):
    """Detailed service health information."""
    
    @blp.response(200, {'services': fields.Dict(fields.Nested(ServiceHealthSchema))})
    def get(self):
        """Get detailed health information for all backend services.
        
        Returns comprehensive health data for each configured service
        including response times, URLs, and detailed status information.
        """
        try:
            service_details = {}
            
            for service_name, service_config in current_app.config['SERVICES'].items():
                start_time = time.time()
                is_healthy = service_client.health_check(service_name)
                response_time = (time.time() - start_time) * 1000
                
                service_details[service_name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'response_time_ms': round(response_time, 2),
                    'last_check': time.time(),
                    'url': service_config['url']
                }
            
            return {'services': service_details}
            
        except Exception as e:
            current_app.logger.error(f"Services health check failed: {str(e)}")
            blp.abort(500, message="Failed to check service health")