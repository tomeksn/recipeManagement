"""Client for communicating with Product Service."""
import structlog
from typing import Optional, Dict, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app

logger = structlog.get_logger("recipe_service.product_client")


class ProductServiceError(Exception):
    """Exception raised when Product Service communication fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ProductClient:
    """Client for communicating with Product Service."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        """Initialize Product Service client.
        
        Args:
            base_url: Base URL of Product Service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or current_app.config['PRODUCT_SERVICE_URL']
        self.timeout = timeout or current_app.config['SERVICE_TIMEOUT']
        
        # Configure session with retry strategy
        self.session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Recipe-Service/1.0'
        })
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID from Product Service.
        
        Args:
            product_id: Product UUID
            
        Returns:
            Product data or None if not found
            
        Raises:
            ProductServiceError: If communication fails
        """
        url = f"{self.base_url}/api/v1/products/{product_id}"
        
        try:
            logger.debug("Fetching product from Product Service", product_id=product_id, url=url)
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 404:
                logger.warning("Product not found", product_id=product_id)
                return None
            
            if response.status_code != 200:
                error_msg = f"Product Service returned {response.status_code}"
                logger.error("Product Service error", 
                           product_id=product_id, 
                           status_code=response.status_code,
                           response_text=response.text)
                raise ProductServiceError(error_msg, response.status_code)
            
            product_data = response.json()
            logger.debug("Product fetched successfully", product_id=product_id)
            
            return product_data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to communicate with Product Service: {str(e)}"
            logger.error("Product Service communication failed", 
                        product_id=product_id, 
                        error=str(e))
            raise ProductServiceError(error_msg)
    
    def get_products_batch(self, product_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get multiple products by IDs (batch operation).
        
        Args:
            product_ids: List of product UUIDs
            
        Returns:
            Dictionary mapping product_id to product data
            
        Raises:
            ProductServiceError: If communication fails
        """
        if not product_ids:
            return {}
        
        # For now, we'll fetch products individually
        # TODO: Implement batch endpoint in Product Service
        products = {}
        
        for product_id in product_ids:
            try:
                product = self.get_product(product_id)
                if product:
                    products[product_id] = product
            except ProductServiceError:
                # Continue with other products, log error
                logger.warning("Failed to fetch product in batch", product_id=product_id)
                continue
        
        logger.info("Batch product fetch completed", 
                   requested=len(product_ids), 
                   fetched=len(products))
        
        return products
    
    def validate_product_exists(self, product_id: str) -> bool:
        """Validate that a product exists in Product Service.
        
        Args:
            product_id: Product UUID
            
        Returns:
            True if product exists, False otherwise
            
        Raises:
            ProductServiceError: If communication fails
        """
        try:
            product = self.get_product(product_id)
            return product is not None
        except ProductServiceError:
            # Re-raise service errors, but treat 404 as False
            raise
    
    def validate_products_exist(self, product_ids: List[str]) -> Dict[str, bool]:
        """Validate that multiple products exist.
        
        Args:
            product_ids: List of product UUIDs
            
        Returns:
            Dictionary mapping product_id to existence status
            
        Raises:
            ProductServiceError: If communication fails
        """
        validation_results = {}
        
        for product_id in product_ids:
            try:
                validation_results[product_id] = self.validate_product_exists(product_id)
            except ProductServiceError:
                logger.warning("Failed to validate product existence", product_id=product_id)
                validation_results[product_id] = False
        
        return validation_results
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search products in Product Service.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of product data
            
        Raises:
            ProductServiceError: If communication fails
        """
        url = f"{self.base_url}/api/v1/products/search"
        params = {'q': query, 'limit': limit}
        
        try:
            logger.debug("Searching products", query=query, limit=limit)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                error_msg = f"Product Service search failed with {response.status_code}"
                logger.error("Product search failed", 
                           query=query,
                           status_code=response.status_code,
                           response_text=response.text)
                raise ProductServiceError(error_msg, response.status_code)
            
            search_data = response.json()
            results = search_data.get('results', [])
            
            logger.debug("Product search completed", 
                        query=query, 
                        results_count=len(results))
            
            return results
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to search products: {str(e)}"
            logger.error("Product search communication failed", 
                        query=query, 
                        error=str(e))
            raise ProductServiceError(error_msg)
    
    def health_check(self) -> bool:
        """Check if Product Service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        url = f"{self.base_url}/health"
        
        try:
            response = self.session.get(url, timeout=5)  # Short timeout for health check
            return response.status_code == 200
        except Exception:
            return False


# Global client instance - lazy initialization
product_client = None

def get_product_client():
    """Get or create product client instance."""
    global product_client
    if product_client is None:
        product_client = ProductClient()
    return product_client