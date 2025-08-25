"""Recipe repository for data access layer."""
import structlog
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from flask import current_app
from sqlalchemy import or_, and_, func, text
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.recipe import (
    Recipe, RecipeIngredient, RecipeVersion, RecipeDependency, 
    RecipeNutrition, RecipeTag, RecipeAudit, RecipeStatus, IngredientUnit
)
from ..utils.exceptions import (
    RecipeNotFoundError, RecipeIngredientNotFoundError, CircularDependencyError,
    RecipeValidationError, MaxDepthExceededError, TooManyIngredientsError
)
from ..services.product_client import get_product_client, ProductServiceError

logger = structlog.get_logger("recipe_service.repository")


class RecipeRepository:
    """Repository for Recipe entity operations."""
    
    def __init__(self):
        self.model = Recipe
        self.session = db.session
    
    def get_by_id(self, recipe_id: UUID, include_relationships: bool = False) -> Optional[Recipe]:
        """Get recipe by ID.
        
        Args:
            recipe_id: Recipe UUID
            include_relationships: Whether to include ingredients and other relationships
            
        Returns:
            Recipe instance or None if not found
        """
        query = self.session.query(self.model)
        
        if include_relationships:
            query = query.options(
                joinedload(Recipe.ingredients),
                joinedload(Recipe.tags),
                joinedload(Recipe.nutrition)
            )
        
        return query.filter(self.model.id == recipe_id).first()
    
    def get_by_product_id(self, product_id: UUID, include_relationships: bool = False) -> Optional[Recipe]:
        """Get recipe by product ID.
        
        Args:
            product_id: Product UUID
            include_relationships: Whether to include ingredients and other relationships
            
        Returns:
            Recipe instance or None if not found
        """
        query = self.session.query(self.model)
        
        if include_relationships:
            query = query.options(
                joinedload(Recipe.ingredients),
                joinedload(Recipe.tags),
                joinedload(Recipe.nutrition)
            )
        
        # Get the active recipe for this product
        return query.filter(
            and_(
                self.model.product_id == product_id,
                self.model.status == RecipeStatus.ACTIVE
            )
        ).first()
    
    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[RecipeStatus] = None,
        product_id: Optional[UUID] = None,
        include_relationships: bool = False
    ) -> Tuple[List[Recipe], Dict[str, Any]]:
        """Get all recipes with filtering and pagination.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            status: Filter by recipe status
            product_id: Filter by product ID
            include_relationships: Whether to include ingredients and tags
            
        Returns:
            Tuple of (recipes list, pagination metadata)
        """
        query = self.session.query(self.model)
        
        # Apply filters
        if status:
            query = query.filter(self.model.status == status)
        
        if product_id:
            query = query.filter(self.model.product_id == product_id)
        
        if include_relationships:
            query = query.options(
                joinedload(Recipe.ingredients),
                joinedload(Recipe.tags),
                joinedload(Recipe.nutrition)
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
    
    def create(self, recipe_data: Dict[str, Any], created_by: Optional[UUID] = None) -> Recipe:
        """Create a new recipe.
        
        Args:
            recipe_data: Recipe data dictionary
            created_by: User ID who created the recipe
            
        Returns:
            Created Recipe instance
            
        Raises:
            RecipeValidationError: If validation fails
            CircularDependencyError: If circular dependency detected
        """
        try:
            # Validate product exists
            product_id = recipe_data['product_id']
            if not get_product_client().validate_product_exists(product_id):
                raise RecipeValidationError(f"Product {product_id} does not exist")
            
            # Create recipe
            recipe = Recipe(
                product_id=product_id,
                name=recipe_data['name'],
                description=recipe_data.get('description'),
                status=RecipeStatus(recipe_data.get('status', 'draft')),
                yield_quantity=recipe_data.get('yield_quantity'),
                yield_unit=IngredientUnit(recipe_data['yield_unit']) if recipe_data.get('yield_unit') else None,
                preparation_time=recipe_data.get('preparation_time'),
                notes=recipe_data.get('notes'),
                created_by=created_by,
                updated_by=created_by
            )
            
            self.session.add(recipe)
            self.session.flush()  # Get the ID
            
            # Handle ingredients
            if 'ingredients' in recipe_data:
                self._create_ingredients(recipe, recipe_data['ingredients'])
            
            # Handle tags
            if 'tag_ids' in recipe_data:
                self._assign_tags(recipe, recipe_data['tag_ids'])
            
            # Validate recipe
            self._validate_recipe(recipe)
            
            # Update dependencies
            self._update_dependencies(recipe)
            
            self.session.commit()
            
            # Create version snapshot
            self._create_version_snapshot(recipe, "Initial version", created_by)
            
            logger.info("Recipe created successfully", recipe_id=str(recipe.id))
            return recipe
            
        except IntegrityError as e:
            self.session.rollback()
            if 'recipes_product_version_unique' in str(e):
                raise RecipeValidationError("Recipe for this product already exists")
            raise
        except (ProductServiceError, RecipeValidationError, CircularDependencyError):
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise
    
    def update(
        self,
        recipe_id: UUID,
        recipe_data: Dict[str, Any],
        updated_by: Optional[UUID] = None
    ) -> Recipe:
        """Update an existing recipe.
        
        Args:
            recipe_id: Recipe UUID
            recipe_data: Updated recipe data
            updated_by: User ID who updated the recipe
            
        Returns:
            Updated Recipe instance
            
        Raises:
            RecipeNotFoundError: If recipe doesn't exist
            RecipeValidationError: If validation fails
        """
        recipe = self.get_by_id(recipe_id, include_relationships=True)
        if not recipe:
            raise RecipeNotFoundError(str(recipe_id))
        
        try:
            # Store old values for version tracking
            old_data = recipe.to_dict(include_relationships=True)
            
            # Update basic fields
            if 'name' in recipe_data:
                recipe.name = recipe_data['name']
            if 'description' in recipe_data:
                recipe.description = recipe_data['description']
            if 'status' in recipe_data:
                recipe.status = RecipeStatus(recipe_data['status'])
            if 'yield_quantity' in recipe_data:
                recipe.yield_quantity = recipe_data['yield_quantity']
            if 'yield_unit' in recipe_data:
                recipe.yield_unit = IngredientUnit(recipe_data['yield_unit']) if recipe_data['yield_unit'] else None
            if 'preparation_time' in recipe_data:
                recipe.preparation_time = recipe_data['preparation_time']
            if 'notes' in recipe_data:
                recipe.notes = recipe_data['notes']
            
            recipe.updated_by = updated_by
            
            # Handle ingredient updates
            if 'ingredients' in recipe_data:
                # Remove existing ingredients
                for ingredient in recipe.ingredients[:]:
                    self.session.delete(ingredient)
                
                # Add new ingredients
                self._create_ingredients(recipe, recipe_data['ingredients'])
            
            # Handle tag updates
            if 'tag_ids' in recipe_data:
                self._assign_tags(recipe, recipe_data['tag_ids'])
            
            # Validate recipe
            self._validate_recipe(recipe)
            
            # Update dependencies
            self._update_dependencies(recipe)
            
            # Increment version if significant changes
            if self._should_increment_version(old_data, recipe_data):
                recipe.version += 1
                change_summary = recipe_data.get('change_summary', 'Recipe updated')
                self._create_version_snapshot(recipe, change_summary, updated_by)
            
            self.session.commit()
            
            logger.info("Recipe updated successfully", recipe_id=str(recipe.id))
            return recipe
            
        except (RecipeValidationError, CircularDependencyError):
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise
    
    def delete(self, recipe_id: UUID) -> bool:
        """Delete a recipe.
        
        Args:
            recipe_id: Recipe UUID
            
        Returns:
            True if deleted, False if not found
        """
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            return False
        
        try:
            self.session.delete(recipe)
            self.session.commit()
            
            logger.info("Recipe deleted successfully", recipe_id=str(recipe_id))
            return True
        except Exception:
            self.session.rollback()
            raise
    
    def get_recipe_hierarchy(self, recipe_id: UUID, max_depth: int = 10, include_product_details: bool = True) -> List[Dict[str, Any]]:
        """Get hierarchical recipe expansion.
        
        Args:
            recipe_id: Recipe UUID
            max_depth: Maximum recursion depth
            include_product_details: Whether to fetch product details from Product Service
            
        Returns:
            List of hierarchical ingredient data
            
        Raises:
            RecipeNotFoundError: If recipe doesn't exist
            MaxDepthExceededError: If max depth exceeded
        """
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundError(str(recipe_id))
        
        try:
            # Use database function for hierarchical query
            result = self.session.execute(
                text("SELECT * FROM recipe_service.calculate_recipe_hierarchy(:recipe_id)"),
                {'recipe_id': recipe_id}
            )
            
            hierarchy = []
            product_ids = set()
            
            for row in result:
                hierarchy_item = {
                    'ingredient_product_id': str(row.ingredient_product_id),
                    'ingredient_name': row.ingredient_name,
                    'quantity': float(row.quantity),
                    'unit': row.unit,
                    'depth_level': row.depth_level,
                    'path': row.path
                }
                hierarchy.append(hierarchy_item)
                product_ids.add(str(row.ingredient_product_id))
            
            # Check depth limit
            max_actual_depth = max([item['depth_level'] for item in hierarchy], default=0)
            if max_actual_depth > max_depth:
                raise MaxDepthExceededError(max_depth)
            
            # Fetch product details if requested
            if include_product_details and product_ids:
                try:
                    product_details = get_product_client().get_products_batch(list(product_ids))
                    
                    # Update hierarchy with product details
                    for item in hierarchy:
                        product_id = item['ingredient_product_id']
                        if product_id in product_details:
                            product = product_details[product_id]
                            item.update({
                                'ingredient_name': product.get('name', item['ingredient_name']),
                                'product_type': product.get('type'),
                                'product_unit': product.get('unit'),
                                'product_description': product.get('description')
                            })
                except ProductServiceError as e:
                    logger.warning("Failed to fetch product details for hierarchy", 
                                 recipe_id=str(recipe_id), 
                                 error=str(e))
                    # Continue without product details
            
            logger.info("Recipe hierarchy calculated", 
                       recipe_id=str(recipe_id),
                       hierarchy_items=len(hierarchy),
                       max_depth=max_actual_depth)
            
            return hierarchy
            
        except Exception:
            logger.error("Error calculating recipe hierarchy", recipe_id=str(recipe_id))
            raise
    
    def validate_recipe(self, recipe_id: UUID) -> Dict[str, Any]:
        """Validate a recipe using database function.
        
        Args:
            recipe_id: Recipe UUID
            
        Returns:
            Validation results
        """
        try:
            result = self.session.execute(
                text("SELECT * FROM recipe_service.validate_recipe(:recipe_id)"),
                {'recipe_id': recipe_id}
            ).first()
            
            return {
                'is_valid': result.is_valid,
                'validation_errors': result.validation_errors or []
            }
            
        except Exception:
            logger.error("Error validating recipe", recipe_id=str(recipe_id))
            return {
                'is_valid': False,
                'validation_errors': ['Validation function failed']
            }
    
    def _create_ingredients(self, recipe: Recipe, ingredients_data: List[Dict[str, Any]]) -> None:
        """Create ingredients for a recipe.
        
        Args:
            recipe: Recipe instance
            ingredients_data: List of ingredient data
        """
        if len(ingredients_data) > current_app.config['MAX_INGREDIENTS_PER_RECIPE']:
            raise TooManyIngredientsError(current_app.config['MAX_INGREDIENTS_PER_RECIPE'])
        
        # Validate all ingredient products exist
        product_ids = [ing['ingredient_product_id'] for ing in ingredients_data]
        validation_results = get_product_client().validate_products_exist(product_ids)
        
        invalid_products = [pid for pid, exists in validation_results.items() if not exists]
        if invalid_products:
            raise RecipeValidationError(f"Invalid product IDs: {invalid_products}")
        
        for idx, ingredient_data in enumerate(ingredients_data):
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=ingredient_data['ingredient_product_id'],
                quantity=ingredient_data['quantity'],
                unit=IngredientUnit(ingredient_data['unit']),
                sort_order=ingredient_data.get('sort_order', idx),
                ingredient_group=ingredient_data.get('ingredient_group'),
                notes=ingredient_data.get('notes'),
                is_optional=ingredient_data.get('is_optional', False),
                substitute_ingredients=ingredient_data.get('substitute_ingredients')
            )
            
            recipe.ingredients.append(ingredient)
    
    def _assign_tags(self, recipe: Recipe, tag_ids: List[UUID]) -> None:
        """Assign tags to a recipe.
        
        Args:
            recipe: Recipe instance
            tag_ids: List of tag UUIDs
        """
        if tag_ids:
            tags = self.session.query(RecipeTag).filter(
                RecipeTag.id.in_(tag_ids)
            ).all()
            recipe.tags = tags
    
    def _validate_recipe(self, recipe: Recipe) -> None:
        """Validate recipe business rules.
        
        Args:
            recipe: Recipe instance
            
        Raises:
            RecipeValidationError: If validation fails
        """
        errors = []
        
        # Must have at least one ingredient
        if not recipe.ingredients:
            errors.append("Recipe must have at least one ingredient")
        
        # Check for required ingredients
        required_ingredients = [ing for ing in recipe.ingredients if not ing.is_optional]
        if not required_ingredients:
            errors.append("Recipe must have at least one required ingredient")
        
        if errors:
            raise RecipeValidationError("Recipe validation failed", {'errors': errors})
    
    def _update_dependencies(self, recipe: Recipe) -> None:
        """Update recipe dependencies tracking.
        
        Args:
            recipe: Recipe instance
        """
        # Remove existing dependencies
        self.session.query(RecipeDependency).filter(
            RecipeDependency.parent_recipe_id == recipe.id
        ).delete()
        
        # Add new dependencies
        for ingredient in recipe.ingredients:
            dependency = RecipeDependency(
                parent_recipe_id=recipe.id,
                child_product_id=ingredient.ingredient_product_id,
                dependency_type='ingredient',
                depth_level=1
            )
            self.session.add(dependency)
    
    def _should_increment_version(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Determine if recipe changes warrant version increment.
        
        Args:
            old_data: Old recipe data
            new_data: New recipe data
            
        Returns:
            True if version should be incremented
        """
        significant_fields = ['ingredients', 'yield_quantity', 'yield_unit']
        
        for field in significant_fields:
            if field in new_data:
                return True
        
        return False
    
    def _create_version_snapshot(self, recipe: Recipe, change_summary: str, created_by: Optional[UUID]) -> None:
        """Create a version snapshot of the recipe.
        
        Args:
            recipe: Recipe instance
            change_summary: Description of changes
            created_by: User who made the changes
        """
        version = RecipeVersion(
            recipe_id=recipe.id,
            version_number=recipe.version,
            recipe_data=recipe.to_dict(include_relationships=True),
            change_summary=change_summary,
            created_by=created_by
        )
        
        self.session.add(version)
    
    def get_recipe_dependencies(self, recipe_id: UUID) -> List[Dict[str, Any]]:
        """Get all dependencies for a recipe.
        
        Args:
            recipe_id: Recipe UUID
            
        Returns:
            List of recipe dependencies
        """
        try:
            dependencies = self.session.query(RecipeDependency).filter(
                RecipeDependency.parent_recipe_id == recipe_id
            ).order_by(RecipeDependency.depth_level).all()
            
            return [dep.to_dict() for dep in dependencies]
            
        except Exception:
            logger.error("Error fetching recipe dependencies", recipe_id=str(recipe_id))
            raise
    
    def get_recipes_using_product(self, product_id: UUID) -> List[Recipe]:
        """Get all recipes that use a specific product as ingredient.
        
        Args:
            product_id: Product UUID
            
        Returns:
            List of recipes using this product
        """
        try:
            recipes = self.session.query(Recipe).join(
                RecipeIngredient,
                Recipe.id == RecipeIngredient.recipe_id
            ).filter(
                RecipeIngredient.ingredient_product_id == product_id
            ).distinct().all()
            
            return recipes
            
        except Exception:
            logger.error("Error finding recipes using product", product_id=str(product_id))
            raise
    
    def get_recipe_complexity_metrics(self, recipe_id: UUID) -> Dict[str, Any]:
        """Calculate complexity metrics for a recipe.
        
        Args:
            recipe_id: Recipe UUID
            
        Returns:
            Dictionary with complexity metrics
        """
        try:
            recipe = self.get_by_id(recipe_id, include_relationships=True)
            if not recipe:
                raise RecipeNotFoundError(str(recipe_id))
            
            # Get hierarchy for complexity analysis
            hierarchy = self.get_recipe_hierarchy(recipe_id, include_product_details=False)
            
            # Calculate metrics
            metrics = {
                'ingredient_count': len(recipe.ingredients),
                'hierarchy_depth': max([item['depth_level'] for item in hierarchy], default=1),
                'total_ingredients_expanded': len(hierarchy),
                'complexity_score': 0,
                'ingredient_groups': len(set(ing.ingredient_group for ing in recipe.ingredients if ing.ingredient_group)),
                'optional_ingredients': len([ing for ing in recipe.ingredients if ing.is_optional]),
                'required_ingredients': len([ing for ing in recipe.ingredients if not ing.is_optional])
            }
            
            # Calculate complexity score
            base_score = metrics['ingredient_count'] * 2
            depth_penalty = (metrics['hierarchy_depth'] - 1) * 5
            group_bonus = metrics['ingredient_groups'] * 1
            
            metrics['complexity_score'] = base_score + depth_penalty - group_bonus
            
            # Classify complexity
            if metrics['complexity_score'] <= 10:
                complexity_level = 'simple'
            elif metrics['complexity_score'] <= 25:
                complexity_level = 'moderate'
            elif metrics['complexity_score'] <= 50:
                complexity_level = 'complex'
            else:
                complexity_level = 'very_complex'
            
            metrics['complexity_level'] = complexity_level
            
            return metrics
            
        except Exception:
            logger.error("Error calculating recipe complexity", recipe_id=str(recipe_id))
            raise


class RecipeIngredientRepository:
    """Repository for RecipeIngredient operations."""
    
    def __init__(self):
        self.model = RecipeIngredient
        self.session = db.session
    
    def get_by_id(self, ingredient_id: UUID) -> Optional[RecipeIngredient]:
        """Get recipe ingredient by ID."""
        return self.session.query(self.model).filter(self.model.id == ingredient_id).first()
    
    def get_by_recipe(self, recipe_id: UUID) -> List[RecipeIngredient]:
        """Get all ingredients for a recipe."""
        return self.session.query(self.model).filter(
            self.model.recipe_id == recipe_id
        ).order_by(self.model.sort_order).all()
    
    def update(self, ingredient_id: UUID, ingredient_data: Dict[str, Any]) -> RecipeIngredient:
        """Update a recipe ingredient.
        
        Args:
            ingredient_id: Ingredient UUID
            ingredient_data: Updated ingredient data
            
        Returns:
            Updated RecipeIngredient instance
            
        Raises:
            RecipeIngredientNotFoundError: If ingredient doesn't exist
        """
        ingredient = self.get_by_id(ingredient_id)
        if not ingredient:
            raise RecipeIngredientNotFoundError(str(ingredient_id))
        
        try:
            # Update fields
            if 'quantity' in ingredient_data:
                ingredient.quantity = ingredient_data['quantity']
            if 'unit' in ingredient_data:
                ingredient.unit = IngredientUnit(ingredient_data['unit'])
            if 'sort_order' in ingredient_data:
                ingredient.sort_order = ingredient_data['sort_order']
            if 'ingredient_group' in ingredient_data:
                ingredient.ingredient_group = ingredient_data['ingredient_group']
            if 'notes' in ingredient_data:
                ingredient.notes = ingredient_data['notes']
            if 'is_optional' in ingredient_data:
                ingredient.is_optional = ingredient_data['is_optional']
            if 'substitute_ingredients' in ingredient_data:
                ingredient.substitute_ingredients = ingredient_data['substitute_ingredients']
            
            self.session.commit()
            return ingredient
            
        except Exception:
            self.session.rollback()
            raise
    
    def delete(self, ingredient_id: UUID) -> bool:
        """Delete a recipe ingredient.
        
        Args:
            ingredient_id: Ingredient UUID
            
        Returns:
            True if deleted, False if not found
        """
        ingredient = self.get_by_id(ingredient_id)
        if not ingredient:
            return False
        
        try:
            self.session.delete(ingredient)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            raise


class RecipeTagRepository:
    """Repository for RecipeTag operations."""
    
    def __init__(self):
        self.model = RecipeTag
        self.session = db.session
    
    def get_all(self) -> List[RecipeTag]:
        """Get all recipe tags."""
        return self.session.query(self.model).order_by(self.model.name).all()
    
    def get_by_id(self, tag_id: UUID) -> Optional[RecipeTag]:
        """Get tag by ID."""
        return self.session.query(self.model).filter(self.model.id == tag_id).first()
    
    def create(self, tag_data: Dict[str, Any]) -> RecipeTag:
        """Create a new tag."""
        tag = RecipeTag(**tag_data)
        self.session.add(tag)
        self.session.commit()
        return tag