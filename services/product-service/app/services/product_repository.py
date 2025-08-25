"""Product repository for data access layer."""
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import or_, and_, func, text
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from ..extensions import db, cache
from ..models.product import (
    Product, ProductCategory, ProductTag, ProductAudit, ProductSearchCache,
    ProductType, ProductUnit
)
from ..utils.exceptions import ProductNotFoundError, ProductAlreadyExistsError


class ProductRepository:
    """Repository for Product entity operations."""
    
    def __init__(self):
        self.model = Product
        self.session = db.session
    
    def get_by_id(self, product_id: UUID, include_relationships: bool = False) -> Optional[Product]:
        """Get product by ID.
        
        Args:
            product_id: Product UUID
            include_relationships: Whether to include categories and tags
            
        Returns:
            Product instance or None if not found
        """
        query = self.session.query(self.model)
        
        if include_relationships:
            query = query.options(
                joinedload(Product.categories),
                joinedload(Product.tags)
            )
        
        return query.filter(self.model.id == product_id).first()
    
    def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name.
        
        Args:
            name: Product name
            
        Returns:
            Product instance or None if not found
        """
        return self.session.query(self.model).filter(
            func.lower(self.model.name) == func.lower(name.strip())
        ).first()
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        product_type: Optional[ProductType] = None,
        product_unit: Optional[ProductUnit] = None,
        category_id: Optional[UUID] = None,
        tag_id: Optional[UUID] = None,
        include_relationships: bool = False
    ) -> Tuple[List[Product], Dict[str, Any]]:
        """Get all products with filtering and pagination.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            product_type: Filter by product type
            product_unit: Filter by product unit
            category_id: Filter by category
            tag_id: Filter by tag
            include_relationships: Whether to include categories and tags
            
        Returns:
            Tuple of (products list, pagination metadata)
        """
        query = self.session.query(self.model)
        
        # Apply filters
        if product_type:
            query = query.filter(self.model.type == product_type)
        
        if product_unit:
            query = query.filter(self.model.unit == product_unit)
        
        if category_id:
            query = query.join(Product.categories).filter(
                ProductCategory.id == category_id
            )
        
        if tag_id:
            query = query.join(Product.tags).filter(
                ProductTag.id == tag_id
            )
        
        if include_relationships:
            query = query.options(
                joinedload(Product.categories),
                joinedload(Product.tags)
            )
        
        # Order by name
        query = query.order_by(self.model.name)
        
        # Paginate
        paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        metadata = {
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_prev': paginated.has_prev,
            'has_next': paginated.has_next,
            'prev_num': paginated.prev_num,
            'next_num': paginated.next_num
        }
        
        return paginated.items, metadata
    
    def create(self, product_data: Dict[str, Any], created_by: Optional[UUID] = None) -> Product:
        """Create a new product.
        
        Args:
            product_data: Product data dictionary
            created_by: User ID who created the product
            
        Returns:
            Created Product instance
            
        Raises:
            ProductAlreadyExistsError: If product name already exists
        """
        # Check if product with same name exists
        existing = self.get_by_name(product_data['name'])
        if existing:
            raise ProductAlreadyExistsError(product_data['name'])
        
        try:
            # Create product
            product = Product(
                name=product_data['name'],
                type=ProductType(product_data.get('type', 'standard')),
                unit=ProductUnit(product_data.get('unit', 'piece')),
                description=product_data.get('description'),
                created_by=created_by,
                updated_by=created_by
            )
            
            self.session.add(product)
            self.session.flush()  # Get the ID
            
            # Handle categories and tags
            self._handle_relationships(product, product_data)
            
            self.session.commit()
            return product
            
        except IntegrityError as e:
            self.session.rollback()
            if 'products_name_unique' in str(e):
                raise ProductAlreadyExistsError(product_data['name'])
            raise
        except Exception:
            self.session.rollback()
            raise
    
    def update(
        self,
        product_id: UUID,
        product_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Product:
        """Update an existing product.
        
        Args:
            product_id: Product UUID
            product_data: Updated product data
            updated_by: User ID who updated the product
            
        Returns:
            Updated Product instance
            
        Raises:
            ProductNotFoundError: If product doesn't exist
            ProductAlreadyExistsError: If new name already exists
        """
        product = self.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(str(product_id))
        
        # Check name uniqueness if name is being changed
        if 'name' in product_data and product_data['name'] != product.name:
            existing = self.get_by_name(product_data['name'])
            if existing and existing.id != product_id:
                raise ProductAlreadyExistsError(product_data['name'])
        
        try:
            # Update basic fields
            if 'name' in product_data:
                product.name = product_data['name']
            if 'type' in product_data:
                product.type = ProductType(product_data['type'])
            if 'unit' in product_data:
                product.unit = ProductUnit(product_data['unit'])
            if 'description' in product_data:
                product.description = product_data['description']
            
            product.updated_by = updated_by
            
            # Handle relationships
            self._handle_relationships(product, product_data)
            
            self.session.commit()
            return product
            
        except IntegrityError as e:
            self.session.rollback()
            if 'products_name_unique' in str(e):
                raise ProductAlreadyExistsError(product_data['name'])
            raise
        except Exception:
            self.session.rollback()
            raise
    
    def delete(self, product_id: UUID) -> bool:
        """Delete a product.
        
        Args:
            product_id: Product UUID
            
        Returns:
            True if deleted, False if not found
        """
        product = self.get_by_id(product_id)
        if not product:
            return False
        
        try:
            self.session.delete(product)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            raise
    
    def search_fuzzy(
        self,
        search_term: str,
        limit: int = 10,
        similarity_threshold: float = 0.3,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Perform fuzzy search on products.
        
        Args:
            search_term: Search term
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold
            use_cache: Whether to use search cache
            
        Returns:
            List of product dictionaries with similarity scores
        """
        if not search_term or not search_term.strip():
            return []
        
        search_term = search_term.strip()
        
        # Check cache first
        if use_cache:
            cached_result = self._get_cached_search_result(search_term, limit, similarity_threshold)
            if cached_result:
                return cached_result
        
        # Perform database search using the fuzzy search function
        try:
            result = self.session.execute(
                text("""
                    SELECT 
                        id,
                        name,
                        type,
                        unit,
                        description,
                        similarity_score
                    FROM product_service.search_products_fuzzy(
                        :search_term,
                        :limit_count,
                        :similarity_threshold
                    )
                """),
                {
                    'search_term': search_term,
                    'limit_count': limit,
                    'similarity_threshold': similarity_threshold
                }
            )
            
            products = []
            for row in result:
                products.append({
                    'id': str(row.id),
                    'name': row.name,
                    'type': row.type,
                    'unit': row.unit,
                    'description': row.description,
                    'similarity_score': float(row.similarity_score)
                })
            
            # Cache the result
            if use_cache and products:
                self._cache_search_result(search_term, limit, similarity_threshold, products)
            
            return products
            
        except Exception as e:
            # Fallback to basic search if fuzzy search fails
            return self._basic_search(search_term, limit)
    
    def _handle_relationships(self, product: Product, product_data: Dict[str, Any]) -> None:
        """Handle category and tag relationships.
        
        Args:
            product: Product instance
            product_data: Product data with possible categories and tags
        """
        # Handle categories
        if 'category_ids' in product_data:
            categories = self.session.query(ProductCategory).filter(
                ProductCategory.id.in_(product_data['category_ids'])
            ).all()
            product.categories = categories
        
        # Handle tags
        if 'tag_ids' in product_data:
            tags = self.session.query(ProductTag).filter(
                ProductTag.id.in_(product_data['tag_ids'])
            ).all()
            product.tags = tags
    
    def _get_cached_search_result(
        self,
        search_term: str,
        limit: int,
        similarity_threshold: float
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached search result.
        
        Args:
            search_term: Search term
            limit: Result limit
            similarity_threshold: Similarity threshold
            
        Returns:
            Cached results or None
        """
        search_hash = self._generate_search_hash(search_term, limit, similarity_threshold)
        
        cached_entry = self.session.query(ProductSearchCache).filter(
            and_(
                ProductSearchCache.search_hash == search_hash,
                ProductSearchCache.expires_at > datetime.utcnow()
            )
        ).first()
        
        if cached_entry:
            return cached_entry.results
        
        return None
    
    def _cache_search_result(
        self,
        search_term: str,
        limit: int,
        similarity_threshold: float,
        results: List[Dict[str, Any]]
    ) -> None:
        """Cache search result.
        
        Args:
            search_term: Search term
            limit: Result limit
            similarity_threshold: Similarity threshold
            results: Search results to cache
        """
        try:
            search_hash = self._generate_search_hash(search_term, limit, similarity_threshold)
            expires_at = datetime.utcnow() + timedelta(seconds=300)  # 5 minutes
            
            # Remove existing cache entry
            self.session.query(ProductSearchCache).filter(
                ProductSearchCache.search_hash == search_hash
            ).delete()
            
            # Add new cache entry
            cache_entry = ProductSearchCache(
                search_hash=search_hash,
                search_term=search_term,
                results=results,
                expires_at=expires_at
            )
            
            self.session.add(cache_entry)
            self.session.commit()
            
        except Exception:
            # Don't fail the main operation if caching fails
            self.session.rollback()
    
    def _generate_search_hash(
        self,
        search_term: str,
        limit: int,
        similarity_threshold: float
    ) -> str:
        """Generate hash for search parameters.
        
        Args:
            search_term: Search term
            limit: Result limit
            similarity_threshold: Similarity threshold
            
        Returns:
            SHA-256 hash of search parameters
        """
        hash_input = f"{search_term.lower()}|{limit}|{similarity_threshold}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _basic_search(self, search_term: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback basic search implementation.
        
        Args:
            search_term: Search term
            limit: Result limit
            
        Returns:
            List of matching products
        """
        products = self.session.query(Product).filter(
            Product.name.ilike(f'%{search_term}%')
        ).order_by(Product.name).limit(limit).all()
        
        return [
            {
                'id': str(p.id),
                'name': p.name,
                'type': p.type.value,
                'unit': p.unit.value,
                'description': p.description,
                'similarity_score': 1.0  # Default score for basic search
            }
            for p in products
        ]
    
    def get_audit_history(self, product_id: UUID, limit: int = 50) -> List[ProductAudit]:
        """Get audit history for a product.
        
        Args:
            product_id: Product UUID
            limit: Maximum number of audit entries
            
        Returns:
            List of audit entries
        """
        return self.session.query(ProductAudit).filter(
            ProductAudit.product_id == product_id
        ).order_by(ProductAudit.changed_at.desc()).limit(limit).all()


class CategoryRepository:
    """Repository for ProductCategory operations."""
    
    def __init__(self):
        self.model = ProductCategory
        self.session = db.session
    
    def get_all(self) -> List[ProductCategory]:
        """Get all categories."""
        return self.session.query(self.model).order_by(self.model.name).all()
    
    def get_by_id(self, category_id: UUID) -> Optional[ProductCategory]:
        """Get category by ID."""
        return self.session.query(self.model).filter(self.model.id == category_id).first()
    
    def create(self, category_data: Dict[str, Any]) -> ProductCategory:
        """Create a new category."""
        category = ProductCategory(**category_data)
        self.session.add(category)
        self.session.commit()
        return category


class TagRepository:
    """Repository for ProductTag operations."""
    
    def __init__(self):
        self.model = ProductTag
        self.session = db.session
    
    def get_all(self) -> List[ProductTag]:
        """Get all tags."""
        return self.session.query(self.model).order_by(self.model.name).all()
    
    def get_by_id(self, tag_id: UUID) -> Optional[ProductTag]:
        """Get tag by ID."""
        return self.session.query(self.model).filter(self.model.id == tag_id).first()
    
    def create(self, tag_data: Dict[str, Any]) -> ProductTag:
        """Create a new tag."""
        tag = ProductTag(**tag_data)
        self.session.add(tag)
        self.session.commit()
        return tag