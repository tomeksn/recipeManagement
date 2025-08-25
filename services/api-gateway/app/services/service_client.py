"""HTTP client for backend service communication."""
import time
import logging
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin, urlparse
import hashlib
import json

import httpx
import structlog
from flask import current_app

from ..extensions import cache
from ..utils.exceptions import (
    ServiceUnavailableError, ServiceTimeoutError, UpstreamServiceError,
    CircuitBreakerOpenError
)

logger = structlog.get_logger(__name__)


class CircuitBreaker:
    """Simple circuit breaker implementation."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED")
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.warning(
                    "Circuit breaker opened",
                    failure_count=self.failure_count,
                    threshold=self.failure_threshold
                )
            
            raise e


class ServiceClient:
    """HTTP client for backend service communication.
    
    Provides methods to communicate with backend microservices
    with automatic retries, circuit breaker, caching, and error handling.
    """
    
    def __init__(self):
        """Initialize the service client."""
        self.services = {}
        self.circuit_breakers = {}
        self._clients = {}
        
    def _get_config(self):
        """Get configuration from Flask app context."""
        if current_app:
            self.services = current_app.config['SERVICES']
            return True
        return False
    
    def _get_client(self, service_name: str) -> httpx.Client:
        """Get or create HTTP client for service."""
        if service_name not in self._clients:
            if not self._get_config():
                raise ServiceUnavailableError(service_name, "Flask application context required")
            
            service_config = self.services.get(service_name)
            if not service_config:
                raise ServiceUnavailableError(service_name, "Service configuration not found")
            
            self._clients[service_name] = httpx.Client(
                base_url=service_config['url'],
                timeout=service_config.get('timeout', 30),
                follow_redirects=True,
                headers={'User-Agent': f'API-Gateway/{current_app.config["API_VERSION"]}'}
            )
            
        return self._clients[service_name]
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service_name not in self.circuit_breakers:
            if current_app:
                failure_threshold = current_app.config.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5)
                recovery_timeout = current_app.config.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 60)
            else:
                failure_threshold = 5
                recovery_timeout = 60
                
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout
            )
        
        return self.circuit_breakers[service_name]
    
    def _generate_cache_key(self, service_name: str, method: str, endpoint: str, 
                           params: Optional[Dict] = None, data: Optional[Dict] = None) -> str:
        """Generate cache key for request.
        
        Args:
            service_name: Target service name
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            
        Returns:
            Cache key string
        """
        cache_data = {
            'service': service_name,
            'method': method,
            'endpoint': endpoint,
            'params': params or {},
            'data': data or {},
            'version': current_app.config.get('API_VERSION', 'v1')
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"gateway:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _should_cache_request(self, method: str, endpoint: str) -> bool:
        """Determine if request should be cached.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            
        Returns:
            True if request should be cached
        """
        # Only cache GET requests
        if method.upper() != 'GET':
            return False
        
        # Don't cache health checks
        if '/health' in endpoint:
            return False
            
        # Don't cache real-time data endpoints
        nocache_patterns = ['/live', '/metrics', '/stats']
        return not any(pattern in endpoint for pattern in nocache_patterns)
    
    def _make_request(self, service_name: str, method: str, endpoint: str,
                     params: Optional[Dict] = None, json_data: Optional[Dict] = None,
                     headers: Optional[Dict] = None, use_cache: bool = True) -> Dict[str, Any]:
        """Make HTTP request to backend service.
        
        Args:
            service_name: Target service name
            method: HTTP method
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            use_cache: Whether to use caching
            
        Returns:
            Response JSON data
            
        Raises:
            ServiceUnavailableError: If service is unavailable
            ServiceTimeoutError: If request times out
            UpstreamServiceError: If service returns an error
        """
        start_time = time.time()
        
        # Check cache first for GET requests
        cache_key = None
        if use_cache and self._should_cache_request(method, endpoint):
            cache_key = self._generate_cache_key(service_name, method, endpoint, params, json_data)
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(
                    "Returning cached response",
                    service=service_name,
                    method=method,
                    endpoint=endpoint,
                    cache_key=cache_key
                )
                return cached_result
        
        # Get service configuration
        service_config = self.services.get(service_name)
        if not service_config:
            raise ServiceUnavailableError(service_name, "Service not configured")
        
        client = self._get_client(service_name)
        circuit_breaker = self._get_circuit_breaker(service_name)
        
        # Prepare request
        request_headers = headers or {}
        retries = service_config.get('retries', 3)
        
        def _execute_request():
            """Execute the actual HTTP request."""
            for attempt in range(retries + 1):
                try:
                    response = client.request(
                        method=method,
                        url=endpoint,
                        params=params,
                        json=json_data,
                        headers=request_headers
                    )
                    
                    duration = (time.time() - start_time) * 1000
                    
                    logger.info(
                        "Service request completed",
                        service=service_name,
                        method=method,
                        endpoint=endpoint,
                        status_code=response.status_code,
                        duration_ms=round(duration, 2),
                        attempt=attempt + 1
                    )
                    
                    # Handle different response status codes
                    if response.status_code == 404:
                        return None  # Not found is not an error for the gateway
                    
                    response.raise_for_status()
                    
                    # Parse response
                    if response.headers.get('content-type', '').startswith('application/json'):
                        result = response.json()
                    else:
                        result = {'data': response.text, 'content_type': response.headers.get('content-type')}
                    
                    # Cache successful GET responses
                    if cache_key and response.status_code == 200:
                        cache_ttl = current_app.config.get('CACHE_TTL', 300)
                        cache.set(cache_key, result, timeout=cache_ttl)
                        logger.debug(
                            "Cached response",
                            service=service_name,
                            cache_key=cache_key,
                            cache_ttl=cache_ttl
                        )
                    
                    return result
                    
                except httpx.TimeoutException as e:
                    logger.warning(
                        "Service request timeout",
                        service=service_name,
                        method=method,
                        endpoint=endpoint,
                        attempt=attempt + 1,
                        max_attempts=retries + 1,
                        error=str(e)
                    )
                    if attempt == retries:
                        raise ServiceTimeoutError(service_name, service_config.get('timeout', 30))
                
                except httpx.HTTPStatusError as e:
                    logger.error(
                        "Service HTTP error",
                        service=service_name,
                        method=method,
                        endpoint=endpoint,
                        status_code=e.response.status_code,
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    
                    # Parse error response if possible
                    error_data = None
                    try:
                        if e.response.headers.get('content-type', '').startswith('application/json'):
                            error_data = e.response.json()
                    except:
                        pass
                    
                    # Don't retry client errors (4xx)
                    if 400 <= e.response.status_code < 500:
                        raise UpstreamServiceError(
                            service_name=service_name,
                            status_code=e.response.status_code,
                            message=str(e),
                            upstream_response=error_data
                        )
                    
                    if attempt == retries:
                        raise UpstreamServiceError(
                            service_name=service_name,
                            status_code=e.response.status_code,
                            message=f"Service error after {retries + 1} attempts: {str(e)}",
                            upstream_response=error_data
                        )
                
                except Exception as e:
                    logger.error(
                        "Service request failed",
                        service=service_name,
                        method=method,
                        endpoint=endpoint,
                        attempt=attempt + 1,
                        error=str(e),
                        error_type=type(e).__name__
                    )
                    if attempt == retries:
                        raise ServiceUnavailableError(service_name, f"Communication failed: {str(e)}")
                
                # Exponential backoff for retries
                if attempt < retries:
                    backoff_factor = current_app.config.get('SERVICE_BACKOFF_FACTOR', 0.3)
                    wait_time = (2 ** attempt) * backoff_factor
                    time.sleep(wait_time)
        
        # Execute request with circuit breaker
        try:
            return circuit_breaker.call(_execute_request)
        except CircuitBreakerOpenError:
            raise ServiceUnavailableError(service_name, "Circuit breaker is open")
    
    def health_check(self, service_name: str) -> bool:
        """Check if service is healthy.
        
        Args:
            service_name: Service to check
            
        Returns:
            True if service is healthy
        """
        try:
            if not self._get_config():
                return False
            
            service_config = self.services.get(service_name)
            if not service_config:
                return False
            
            health_endpoint = service_config.get('health_endpoint', '/health')
            response = self._make_request(service_name, 'GET', health_endpoint, use_cache=False)
            
            if response is None:
                return False
                
            return response.get('status') in ['healthy', 'degraded']
            
        except Exception as e:
            logger.warning(
                "Health check failed",
                service=service_name,
                error=str(e)
            )
            return False
    
    def health_check_all(self) -> Dict[str, bool]:
        """Check health of all configured services.
        
        Returns:
            Dictionary mapping service names to health status
        """
        if not self._get_config():
            return {}
        
        results = {}
        for service_name in self.services.keys():
            results[service_name] = self.health_check(service_name)
        return results
    
    def get(self, service_name: str, endpoint: str, params: Optional[Dict] = None,
            headers: Optional[Dict] = None, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Make GET request to service."""
        return self._make_request(service_name, 'GET', endpoint, params=params, 
                                 headers=headers, use_cache=use_cache)
    
    def post(self, service_name: str, endpoint: str, json_data: Optional[Dict] = None,
             params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make POST request to service."""
        return self._make_request(service_name, 'POST', endpoint, params=params,
                                 json_data=json_data, headers=headers, use_cache=False)
    
    def put(self, service_name: str, endpoint: str, json_data: Optional[Dict] = None,
            params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make PUT request to service."""
        return self._make_request(service_name, 'PUT', endpoint, params=params,
                                 json_data=json_data, headers=headers, use_cache=False)
    
    def delete(self, service_name: str, endpoint: str, params: Optional[Dict] = None,
               headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make DELETE request to service."""
        return self._make_request(service_name, 'DELETE', endpoint, params=params,
                                 headers=headers, use_cache=False)
    
    def close_all(self):
        """Close all HTTP clients."""
        for client in self._clients.values():
            client.close()
        self._clients.clear()


# Global client instance
service_client = ServiceClient()