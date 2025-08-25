"""HTTP client for Recipe Service communication."""
import logging
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import httpx
import structlog
from flask import current_app

logger = structlog.get_logger(__name__)


class RecipeServiceError(Exception):
    """Exception raised when Recipe Service communication fails."""
    pass


class RecipeServiceClient:
    """HTTP client for Recipe Service communication.
    
    Provides methods to fetch recipe data from the Recipe Service
    with automatic retries, caching, and error handling.
    """
    
    def __init__(self):
        """Initialize the Recipe Service client."""
        self.base_url = None
        self.timeout = None
        self.retries = None
        self._client = None
    
    def _get_config(self):
        """Get configuration from Flask app context."""
        if not current_app:
            raise RecipeServiceError("Flask application context required")
        
        self.base_url = current_app.config['RECIPE_SERVICE_URL']
        self.timeout = current_app.config['RECIPE_SERVICE_TIMEOUT']
        self.retries = current_app.config['RECIPE_SERVICE_RETRIES']
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            self._get_config()
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON data
            
        Raises:
            RecipeServiceError: If request fails after retries
        """
        client = self._get_client()
        url = endpoint
        
        for attempt in range(self.retries + 1):
            try:
                start_time = time.time()
                response = client.request(method, url, **kwargs)
                duration = (time.time() - start_time) * 1000
                
                logger.info(
                    "Recipe service request",
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    duration_ms=round(duration, 2),
                    attempt=attempt + 1
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.TimeoutException as e:
                logger.warning(
                    "Recipe service timeout",
                    method=method,
                    url=url,
                    attempt=attempt + 1,
                    max_attempts=self.retries + 1,
                    error=str(e)
                )
                if attempt == self.retries:
                    raise RecipeServiceError(f"Recipe service timeout after {self.retries + 1} attempts: {str(e)}")
                
            except httpx.HTTPStatusError as e:
                logger.error(
                    "Recipe service HTTP error",
                    method=method,
                    url=url,
                    status_code=e.response.status_code,
                    attempt=attempt + 1,
                    error=str(e)
                )
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise RecipeServiceError(f"Recipe service client error: {e.response.status_code} - {str(e)}")
                
                if attempt == self.retries:
                    raise RecipeServiceError(f"Recipe service error after {self.retries + 1} attempts: {str(e)}")
                
            except Exception as e:
                logger.error(
                    "Recipe service request failed",
                    method=method,
                    url=url,
                    attempt=attempt + 1,
                    error=str(e)
                )
                if attempt == self.retries:
                    raise RecipeServiceError(f"Recipe service communication failed: {str(e)}")
            
            # Exponential backoff for retries
            if attempt < self.retries:
                wait_time = (2 ** attempt) * 0.1  # 0.1s, 0.2s, 0.4s, etc.
                time.sleep(wait_time)
    
    def health_check(self) -> bool:
        """Check if Recipe Service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = self._make_request('GET', '/health')
            return response.get('status') in ['healthy', 'degraded']
        except Exception:
            return False
    
    def get_recipe(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get recipe for a product.
        
        Args:
            product_id: UUID of the product
            
        Returns:
            Recipe data or None if not found
            
        Raises:
            RecipeServiceError: If request fails
        """
        try:
            return self._make_request('GET', f'/api/v1/recipes/product/{product_id}')
        except RecipeServiceError as e:
            if "404" in str(e):
                return None
            raise
    
    def get_recipe_hierarchy(self, product_id: str, target_quantity: float = None, 
                           max_depth: int = None) -> Optional[Dict[str, Any]]:
        """Get expanded recipe hierarchy for a product.
        
        Args:
            product_id: UUID of the product
            target_quantity: Target quantity for scaling
            max_depth: Maximum expansion depth
            
        Returns:
            Hierarchical recipe data or None if not found
            
        Raises:
            RecipeServiceError: If request fails
        """
        try:
            params = {}
            if target_quantity is not None:
                params['target_quantity'] = target_quantity
            if max_depth is not None:
                params['max_depth'] = max_depth
            
            return self._make_request(
                'GET', 
                f'/api/v1/recipes/product/{product_id}/hierarchy',
                params=params
            )
        except RecipeServiceError as e:
            if "404" in str(e):
                return None
            raise
    
    def get_multiple_recipes(self, product_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get recipes for multiple products.
        
        Args:
            product_ids: List of product UUIDs
            
        Returns:
            Dictionary mapping product_id to recipe data (None if not found)
            
        Raises:
            RecipeServiceError: If request fails
        """
        try:
            response = self._make_request(
                'POST',
                '/api/v1/recipes/batch',
                json={'product_ids': product_ids}
            )
            return response.get('recipes', {})
        except RecipeServiceError as e:
            if "404" in str(e):
                return {pid: None for pid in product_ids}
            raise
    
    def validate_recipe_structure(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recipe structure for circular dependencies.
        
        Args:
            recipe_data: Recipe data to validate
            
        Returns:
            Validation result
            
        Raises:
            RecipeServiceError: If request fails
        """
        return self._make_request(
            'POST',
            '/api/v1/recipes/validate',
            json=recipe_data
        )
    
    def close(self):
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


# Global client instance - lazy initialization  
recipe_client = None

def get_recipe_client():
    """Get or create recipe client instance."""
    global recipe_client
    if recipe_client is None:
        recipe_client = RecipeServiceClient()
    return recipe_client