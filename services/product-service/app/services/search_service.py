"""Advanced search service for products."""
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, or_, and_, text
from sqlalchemy.orm import joinedload

from ..extensions import db, cache
from ..models.product import Product, ProductSearchCache, ProductType, ProductUnit
from ..services.product_repository import ProductRepository


class ProductSearchService:
    """Advanced search service for products with additional features."""
    
    def __init__(self):
        self.repository = ProductRepository()
    
    def advanced_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        similarity_threshold: float = 0.3,
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """Perform advanced product search with filters and suggestions.
        
        Args:
            query: Search query string
            filters: Additional filters (type, unit, category_id, tag_id)
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            include_suggestions: Whether to include search suggestions
            
        Returns:
            Dictionary with search results, suggestions, and metadata
        """
        filters = filters or {}
        
        # Normalize query
        normalized_query = self._normalize_query(query)
        if not normalized_query:
            return {
                'results': [],
                'suggestions': [],
                'query': query,
                'total_results': 0,
                'search_time_ms': 0
            }
        
        start_time = datetime.utcnow()
        
        # Check cache first
        cache_key = self._generate_advanced_search_cache_key(
            normalized_query, filters, limit, similarity_threshold
        )
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Perform search
        results = self._perform_filtered_search(
            normalized_query, filters, limit, similarity_threshold
        )
        
        # Generate suggestions if requested and few results found
        suggestions = []
        if include_suggestions and len(results) < 3:
            suggestions = self._generate_search_suggestions(normalized_query, limit=5)
        
        # Calculate search time
        search_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        response = {
            'results': results,
            'suggestions': suggestions,
            'query': query,
            'normalized_query': normalized_query,
            'total_results': len(results),
            'search_time_ms': search_time_ms,
            'filters_applied': filters
        }
        
        # Cache the result
        self._cache_result(cache_key, response)
        
        return response
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query.
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        if not partial_query or len(partial_query.strip()) < 2:
            return []
        
        normalized_query = self._normalize_query(partial_query)
        
        try:
            # Get products that start with or contain the query
            products = db.session.query(Product.name).filter(
                or_(
                    Product.name.ilike(f'{normalized_query}%'),
                    Product.name.ilike(f'%{normalized_query}%')
                )
            ).distinct().limit(limit * 2).all()
            
            suggestions = []
            for product in products:
                name = product.name
                # Add the full name
                if name not in suggestions:
                    suggestions.append(name)
                
                # Add individual words from the name
                words = name.split()
                for word in words:
                    if (len(word) >= 3 and 
                        word.lower().startswith(normalized_query.lower()) and 
                        word not in suggestions):
                        suggestions.append(word)
                
                if len(suggestions) >= limit:
                    break
            
            return suggestions[:limit]
            
        except Exception:
            return []
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular search terms based on search cache.
        
        Args:
            limit: Maximum number of popular searches
            
        Returns:
            List of popular search terms with counts
        """
        try:
            # Query search cache for frequent terms
            popular_searches = db.session.query(
                ProductSearchCache.search_term,
                func.count(ProductSearchCache.search_term).label('search_count')
            ).filter(
                ProductSearchCache.created_at >= datetime.utcnow() - timedelta(days=30)
            ).group_by(
                ProductSearchCache.search_term
            ).order_by(
                func.count(ProductSearchCache.search_term).desc()
            ).limit(limit).all()
            
            return [
                {
                    'term': search.search_term,
                    'count': search.search_count
                }
                for search in popular_searches
            ]
            
        except Exception:
            return []
    
    def _normalize_query(self, query: str) -> str:
        """Normalize search query.
        
        Args:
            query: Raw search query
            
        Returns:
            Normalized query string
        """
        if not query:
            return ""
        
        # Remove extra whitespace and convert to lowercase
        normalized = re.sub(r'\s+', ' ', query.strip().lower())
        
        # Remove special characters but keep alphanumeric and spaces
        normalized = re.sub(r'[^a-zA-Z0-9\s-]', '', normalized)
        
        return normalized
    
    def _perform_filtered_search(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int,
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Perform filtered search combining fuzzy search with filters.
        
        Args:
            query: Normalized search query
            filters: Search filters
            limit: Result limit
            similarity_threshold: Similarity threshold
            
        Returns:
            List of matching products
        """
        try:
            # Start with basic fuzzy search
            base_results = self.repository.search_fuzzy(
                search_term=query,
                limit=limit * 3,  # Get more results to filter
                similarity_threshold=similarity_threshold,
                use_cache=False  # We handle caching at this level
            )
            
            if not filters:
                return base_results[:limit]
            
            # Apply additional filters
            filtered_results = []
            
            for result in base_results:
                # Get full product for filtering
                product = self.repository.get_by_id(result['id'])
                if not product:
                    continue
                
                # Apply filters
                if self._matches_filters(product, filters):
                    filtered_results.append(result)
                
                if len(filtered_results) >= limit:
                    break
            
            return filtered_results
            
        except Exception:
            # Fallback to basic search
            return self.repository._basic_search(query, limit)
    
    def _matches_filters(self, product: Product, filters: Dict[str, Any]) -> bool:
        """Check if product matches the given filters.
        
        Args:
            product: Product instance
            filters: Filter criteria
            
        Returns:
            True if product matches all filters
        """
        # Type filter
        if 'type' in filters:
            if product.type.value != filters['type']:
                return False
        
        # Unit filter
        if 'unit' in filters:
            if product.unit.value != filters['unit']:
                return False
        
        # Category filter
        if 'category_id' in filters:
            category_ids = [str(cat.id) for cat in product.categories]
            if str(filters['category_id']) not in category_ids:
                return False
        
        # Tag filter
        if 'tag_id' in filters:
            tag_ids = [str(tag.id) for tag in product.tags]
            if str(filters['tag_id']) not in tag_ids:
                return False
        
        return True
    
    def _generate_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Generate search suggestions for queries with few results.
        
        Args:
            query: Original search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        suggestions = []
        
        try:
            # Get similar product names
            similar_products = db.session.query(Product.name).filter(
                or_(
                    func.soundex(Product.name) == func.soundex(query),
                    Product.name.ilike(f'%{query[:-1]}%'),  # Remove last character
                    Product.name.ilike(f'%{query[1:]}%')   # Remove first character
                )
            ).distinct().limit(limit).all()
            
            for product in similar_products:
                if product.name not in suggestions:
                    suggestions.append(product.name)
            
            # Add common typo corrections
            typo_corrections = self._get_typo_corrections(query)
            for correction in typo_corrections:
                if correction not in suggestions and len(suggestions) < limit:
                    suggestions.append(correction)
            
        except Exception:
            pass
        
        return suggestions[:limit]
    
    def _get_typo_corrections(self, query: str) -> List[str]:
        """Get common typo corrections for a query.
        
        Args:
            query: Search query
            
        Returns:
            List of possible typo corrections
        """
        corrections = []
        
        # Common replacements
        common_typos = {
            'recpie': 'recipe',
            'recipie': 'recipe',
            'produkt': 'product',
            'produt': 'product',
            'standart': 'standard',
            'standar': 'standard',
        }
        
        query_lower = query.lower()
        if query_lower in common_typos:
            corrections.append(common_typos[query_lower])
        
        return corrections
    
    def _generate_advanced_search_cache_key(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int,
        similarity_threshold: float
    ) -> str:
        """Generate cache key for advanced search.
        
        Args:
            query: Search query
            filters: Search filters
            limit: Result limit
            similarity_threshold: Similarity threshold
            
        Returns:
            Cache key string
        """
        # Create a stable string representation of filters
        filter_str = ""
        if filters:
            sorted_filters = sorted(filters.items())
            filter_str = "|".join([f"{k}:{v}" for k, v in sorted_filters])
        
        cache_input = f"advanced:{query}|{filter_str}|{limit}|{similarity_threshold}"
        return hashlib.sha256(cache_input.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached result or None
        """
        try:
            cached_entry = db.session.query(ProductSearchCache).filter(
                and_(
                    ProductSearchCache.search_hash == cache_key,
                    ProductSearchCache.expires_at > datetime.utcnow()
                )
            ).first()
            
            if cached_entry:
                return cached_entry.results
            
        except Exception:
            pass
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache search result.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=300)  # 5 minutes
            
            # Remove existing cache entry
            db.session.query(ProductSearchCache).filter(
                ProductSearchCache.search_hash == cache_key
            ).delete()
            
            # Add new cache entry
            cache_entry = ProductSearchCache(
                search_hash=cache_key,
                search_term=result.get('query', ''),
                results=result,
                expires_at=expires_at
            )
            
            db.session.add(cache_entry)
            db.session.commit()
            
        except Exception:
            # Don't fail the main operation if caching fails
            db.session.rollback()
    
    def cleanup_expired_cache(self) -> int:
        """Clean up expired search cache entries.
        
        Returns:
            Number of entries cleaned up
        """
        try:
            deleted_count = db.session.query(ProductSearchCache).filter(
                ProductSearchCache.expires_at < datetime.utcnow()
            ).delete()
            
            db.session.commit()
            return deleted_count
            
        except Exception:
            db.session.rollback()
            return 0