"""Core calculation service for recipe scaling and ingredient calculations."""
import time
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Union
import hashlib
import json

import structlog
from flask import current_app

from .recipe_client import get_recipe_client, RecipeServiceError
from ..extensions import cache
from ..utils.exceptions import (
    CalculationError, InvalidScaleFactorError, RecipeNotFoundError,
    InvalidInputError, MaxIngredientsExceededError
)

logger = structlog.get_logger(__name__)


class CalculationService:
    """Service for performing recipe calculations and scaling."""
    
    def __init__(self):
        """Initialize the calculation service."""
        self.cache_enabled = True
        self.precision_places = 3
        self.max_scale_factor = 1000.0
        self.min_scale_factor = 0.001
        self.max_ingredients = 1000
    
    def _get_config(self):
        """Get configuration from Flask app context."""
        if current_app:
            self.precision_places = current_app.config.get('PRECISION_DECIMAL_PLACES', 3)
            self.max_scale_factor = current_app.config.get('MAX_SCALE_FACTOR', 1000.0)
            self.min_scale_factor = current_app.config.get('MIN_SCALE_FACTOR', 0.001)
            self.max_ingredients = current_app.config.get('MAX_INGREDIENTS_PER_CALCULATION', 1000)
            self.cache_enabled = current_app.config.get('ENABLE_RESULT_CACHING', True)
    
    def _generate_cache_key(self, product_id: str, target_quantity: float, 
                           target_unit: str, include_hierarchy: bool = False,
                           max_depth: int = 5) -> str:
        """Generate cache key for calculation result.
        
        Args:
            product_id: Product UUID
            target_quantity: Target quantity
            target_unit: Target unit
            include_hierarchy: Include hierarchical expansion
            max_depth: Maximum hierarchy depth
            
        Returns:
            Cache key string
        """
        cache_data = {
            'product_id': product_id,
            'target_quantity': target_quantity,
            'target_unit': target_unit,
            'include_hierarchy': include_hierarchy,
            'max_depth': max_depth,
            'version': 'v1'
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"calc:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _round_quantity(self, quantity: Union[float, Decimal], unit: str, 
                       precision: Optional[int] = None) -> float:
        """Round quantity according to unit and precision rules.
        
        Args:
            quantity: Quantity to round
            unit: Unit type ('piece' or 'gram')
            precision: Custom precision (overrides default)
            
        Returns:
            Rounded quantity
        """
        if precision is None:
            precision = self.precision_places
        
        # Convert to Decimal for precise calculations
        if not isinstance(quantity, Decimal):
            quantity = Decimal(str(quantity))
        
        if unit == 'piece':
            # Round pieces to nearest whole number for quantities >= 1
            # Use 1 decimal place for quantities < 1
            if quantity >= 1:
                return float(quantity.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            else:
                return float(quantity.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        else:  # gram
            # Use specified precision for grams
            if precision == 0:
                return float(quantity.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            else:
                places = '0.' + '0' * (precision - 1) + '1'
                return float(quantity.quantize(Decimal(places), rounding=ROUND_HALF_UP))
    
    def _validate_scale_factor(self, scale_factor: float) -> None:
        """Validate scale factor is within acceptable range.
        
        Args:
            scale_factor: Scale factor to validate
            
        Raises:
            InvalidScaleFactorError: If scale factor is invalid
        """
        if not isinstance(scale_factor, (int, float)) or scale_factor <= 0:
            raise InvalidScaleFactorError(f"Scale factor must be a positive number, got: {scale_factor}")
        
        if scale_factor > self.max_scale_factor:
            raise InvalidScaleFactorError(
                f"Scale factor {scale_factor} exceeds maximum allowed: {self.max_scale_factor}"
            )
        
        if scale_factor < self.min_scale_factor:
            raise InvalidScaleFactorError(
                f"Scale factor {scale_factor} below minimum allowed: {self.min_scale_factor}"
            )
    
    def _calculate_scale_factor(self, original_quantity: float, original_unit: str,
                               target_quantity: float, target_unit: str) -> float:
        """Calculate scale factor for recipe scaling.
        
        Args:
            original_quantity: Original recipe quantity
            original_unit: Original recipe unit
            target_quantity: Target quantity
            target_unit: Target unit
            
        Returns:
            Scale factor
            
        Raises:
            InvalidInputError: If units are incompatible or quantities invalid
        """
        if original_quantity <= 0:
            raise InvalidInputError(f"Original quantity must be positive, got: {original_quantity}")
        
        if target_quantity <= 0:
            raise InvalidInputError(f"Target quantity must be positive, got: {target_quantity}")
        
        # Units must match for scaling
        if original_unit != target_unit:
            raise InvalidInputError(
                f"Cannot scale from {original_unit} to {target_unit}. Units must match."
            )
        
        scale_factor = target_quantity / original_quantity
        self._validate_scale_factor(scale_factor)
        
        return scale_factor
    
    def _scale_ingredient(self, ingredient: Dict[str, Any], scale_factor: float,
                         precision: Optional[int] = None) -> Dict[str, Any]:
        """Scale a single ingredient quantity.
        
        Args:
            ingredient: Ingredient data
            scale_factor: Scale factor to apply
            precision: Decimal precision
            
        Returns:
            Scaled ingredient data
        """
        original_quantity = ingredient['quantity']
        unit = ingredient['unit']
        
        # Apply scale factor
        scaled_quantity = original_quantity * scale_factor
        
        # Round according to unit rules
        rounded_quantity = self._round_quantity(scaled_quantity, unit, precision)
        
        return {
            'product_id': ingredient['product_id'],
            'product_name': ingredient.get('product_name', ''),
            'original_quantity': original_quantity,
            'calculated_quantity': rounded_quantity,
            'unit': unit,
            'order': ingredient.get('order', 0)
        }
    
    def _scale_recipe_ingredients(self, recipe_data: Dict[str, Any], scale_factor: float,
                                 precision: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scale all ingredients in a recipe.
        
        Args:
            recipe_data: Recipe data from Recipe Service
            scale_factor: Scale factor to apply
            precision: Decimal precision
            
        Returns:
            List of scaled ingredients
            
        Raises:
            MaxIngredientsExceededError: If too many ingredients
        """
        ingredients = recipe_data.get('ingredients', [])
        
        if len(ingredients) > self.max_ingredients:
            raise MaxIngredientsExceededError(self.max_ingredients)
        
        scaled_ingredients = []
        for ingredient in ingredients:
            scaled_ingredient = self._scale_ingredient(ingredient, scale_factor, precision)
            scaled_ingredients.append(scaled_ingredient)
        
        return scaled_ingredients
    
    def _expand_hierarchical_recipe(self, recipe_data: Dict[str, Any], scale_factor: float,
                                   max_depth: int = 5, current_depth: int = 0,
                                   precision: Optional[int] = None) -> List[Dict[str, Any]]:
        """Expand recipe hierarchy to show sub-recipe ingredients.
        
        Args:
            recipe_data: Recipe data
            scale_factor: Scale factor to apply
            max_depth: Maximum expansion depth
            current_depth: Current recursion depth
            precision: Decimal precision
            
        Returns:
            Expanded ingredient list with hierarchical structure
        """
        if current_depth >= max_depth:
            logger.warning(
                "Maximum hierarchy depth reached",
                max_depth=max_depth,
                current_depth=current_depth
            )
            return self._scale_recipe_ingredients(recipe_data, scale_factor, precision)
        
        expanded_ingredients = []
        ingredients = recipe_data.get('ingredients', [])
        
        for ingredient in ingredients:
            # Scale the ingredient
            scaled_ingredient = self._scale_ingredient(ingredient, scale_factor, precision)
            
            # Check if this ingredient is a semi-product with its own recipe
            product_id = ingredient['product_id']
            try:
                sub_recipe = get_recipe_client().get_recipe(product_id)
                if sub_recipe and sub_recipe.get('product', {}).get('type') == 'semi-product':
                    # Calculate sub-recipe scale factor
                    ingredient_quantity = scaled_ingredient['calculated_quantity']
                    sub_recipe_yield = sub_recipe.get('yield_quantity', 1.0)
                    
                    if sub_recipe_yield > 0:
                        sub_scale_factor = ingredient_quantity / sub_recipe_yield
                        
                        # Recursively expand sub-recipe
                        sub_ingredients = self._expand_hierarchical_recipe(
                            sub_recipe,
                            sub_scale_factor,
                            max_depth,
                            current_depth + 1,
                            precision
                        )
                        
                        # Add hierarchical structure
                        scaled_ingredient['sub_ingredients'] = sub_ingredients
                        scaled_ingredient['expanded'] = True
                        scaled_ingredient['depth'] = current_depth
                    
            except RecipeServiceError:
                # If sub-recipe can't be fetched, treat as regular ingredient
                logger.warning(
                    "Failed to fetch sub-recipe for hierarchical expansion",
                    product_id=product_id
                )
            
            expanded_ingredients.append(scaled_ingredient)
        
        return expanded_ingredients
    
    def calculate_recipe(self, product_id: str, target_quantity: float, target_unit: str,
                        include_hierarchy: bool = False, max_depth: int = 5,
                        precision: Optional[int] = None) -> Dict[str, Any]:
        """Calculate scaled recipe ingredients.
        
        Args:
            product_id: Product UUID
            target_quantity: Target quantity
            target_unit: Target unit ('piece' or 'gram')
            include_hierarchy: Include hierarchical expansion
            max_depth: Maximum hierarchy depth
            precision: Decimal precision override
            
        Returns:
            Calculation result with scaled ingredients
            
        Raises:
            RecipeNotFoundError: If recipe not found
            CalculationError: If calculation fails
        """
        start_time = time.time()
        self._get_config()
        
        # Check cache first
        cache_key = None
        if self.cache_enabled:
            cache_key = self._generate_cache_key(
                product_id, target_quantity, target_unit, include_hierarchy, max_depth
            )
            cached_result = cache.get(cache_key)
            if cached_result:
                cached_result['cached'] = True
                cached_result['calculation_time_ms'] = round((time.time() - start_time) * 1000, 2)
                logger.info(
                    "Returning cached calculation result",
                    product_id=product_id,
                    cache_key=cache_key
                )
                return cached_result
        
        try:
            # Fetch recipe data
            recipe_data = get_recipe_client().get_recipe(product_id)
            if not recipe_data:
                raise RecipeNotFoundError(product_id)
            
            # Get recipe yield information
            recipe_yield = recipe_data.get('yield_quantity', 1.0)
            recipe_yield_unit = recipe_data.get('yield_unit', target_unit)
            
            # Calculate scale factor
            scale_factor = self._calculate_scale_factor(
                recipe_yield, recipe_yield_unit, target_quantity, target_unit
            )
            
            # Scale ingredients
            if include_hierarchy:
                ingredients = self._expand_hierarchical_recipe(
                    recipe_data, scale_factor, max_depth, 0, precision
                )
            else:
                ingredients = self._scale_recipe_ingredients(recipe_data, scale_factor, precision)
            
            # Prepare result
            calculation_time = round((time.time() - start_time) * 1000, 2)
            
            result = {
                'product_id': product_id,
                'product_name': recipe_data.get('product', {}).get('name', ''),
                'target_quantity': target_quantity,
                'target_unit': target_unit,
                'scale_factor': round(scale_factor, 6),
                'original_yield': recipe_yield,
                'original_yield_unit': recipe_yield_unit,
                'ingredients': ingredients,
                'calculation_metadata': {
                    'include_hierarchy': include_hierarchy,
                    'max_depth': max_depth,
                    'precision': precision or self.precision_places,
                    'ingredient_count': len(ingredients),
                    'algorithm_version': 'v1.0'
                },
                'cached': False,
                'calculation_time_ms': calculation_time
            }
            
            # Cache result
            if self.cache_enabled and cache_key:
                cache_ttl = current_app.config.get('CALCULATION_CACHE_TTL', 1800)
                cache.set(cache_key, result, timeout=cache_ttl)
                logger.info(
                    "Cached calculation result",
                    product_id=product_id,
                    cache_key=cache_key,
                    cache_ttl=cache_ttl
                )
            
            # Log calculation history (simplified for now)
            self._log_calculation_history(result)
            
            return result
            
        except RecipeServiceError as e:
            logger.error(
                "Recipe service error during calculation",
                product_id=product_id,
                error=str(e)
            )
            raise CalculationError(f"Failed to fetch recipe data: {str(e)}")
        
        except Exception as e:
            logger.error(
                "Unexpected error during calculation",
                product_id=product_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise CalculationError(f"Calculation failed: {str(e)}")
    
    def calculate_batch(self, calculations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform batch calculations.
        
        Args:
            calculations: List of calculation requests
            
        Returns:
            Batch calculation results
        """
        start_time = time.time()
        results = []
        errors = []
        
        for i, calc_request in enumerate(calculations):
            try:
                result = self.calculate_recipe(
                    product_id=calc_request['product_id'],
                    target_quantity=calc_request['target_quantity'],
                    target_unit=calc_request['target_unit'],
                    include_hierarchy=calc_request.get('include_hierarchy', False),
                    max_depth=calc_request.get('max_depth', 5),
                    precision=calc_request.get('precision')
                )
                results.append(result)
                
            except Exception as e:
                error_info = {
                    'index': i,
                    'product_id': calc_request.get('product_id'),
                    'error': str(e),
                    'error_type': type(e).__name__
                }
                errors.append(error_info)
                logger.error(
                    "Batch calculation item failed",
                    **error_info
                )
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'results': results,
            'summary': {
                'total_requests': len(calculations),
                'successful': len(results),
                'failed': len(errors),
                'total_time_ms': total_time,
                'average_time_ms': round(total_time / len(calculations), 2) if calculations else 0,
                'errors': errors
            }
        }
    
    def _log_calculation_history(self, result: Dict[str, Any]) -> None:
        """Log calculation to history (simplified implementation).
        
        Args:
            result: Calculation result to log
        """
        # For now, just log to structured logger
        # In a full implementation, this would save to database
        logger.info(
            "Calculation completed",
            product_id=result['product_id'],
            target_quantity=result['target_quantity'],
            target_unit=result['target_unit'],
            scale_factor=result['scale_factor'],
            ingredient_count=len(result['ingredients']),
            calculation_time_ms=result['calculation_time_ms'],
            cached=result['cached']
        )
    
    def get_calculation_history(self, product_id: Optional[str] = None,
                               limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get calculation history (placeholder implementation).
        
        Args:
            product_id: Filter by product ID
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of calculation history entries
        """
        # Placeholder implementation - would query database in production
        return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics.
        
        Returns:
            Cache statistics
        """
        try:
            # Basic cache stats (Redis-specific commands would be used in production)
            return {
                'total_keys': 0,  # Would use Redis INFO command
                'hit_rate': 0.0,  # Would track hits/misses
                'memory_usage': {
                    'used_memory': '0MB',
                    'max_memory': 'unlimited'
                },
                'top_products': []  # Would aggregate from cache keys
            }
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {}
    
    def clear_cache(self, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear calculation cache.
        
        Args:
            product_id: Clear cache for specific product only
            
        Returns:
            Clear operation result
        """
        try:
            if product_id:
                # Clear cache for specific product (would use pattern matching in production)
                cleared_keys = 0  # Placeholder
                message = f"Cache cleared for product {product_id}"
            else:
                # Clear all calculation cache
                cache.clear()
                cleared_keys = 0  # Would count actual keys cleared
                message = "All calculation cache cleared"
            
            logger.info("Cache cleared", product_id=product_id, cleared_keys=cleared_keys)
            
            return {
                'cleared_keys': cleared_keys,
                'message': message
            }
            
        except Exception as e:
            logger.error("Failed to clear cache", error=str(e))
            raise CalculationError(f"Cache clear failed: {str(e)}")


# Global service instance
calculation_service = CalculationService()