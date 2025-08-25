"""Recipe resource endpoints."""
import structlog
from datetime import datetime
from uuid import UUID
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError

from ..services.recipe_repository import RecipeRepository, RecipeIngredientRepository, RecipeTagRepository
from ..schemas.recipe import (
    RecipeCreateSchema, RecipeUpdateSchema, RecipeResponseSchema,
    RecipeListSchema, RecipeListQuerySchema, RecipeValidationResponseSchema,
    RecipeHierarchyResponseSchema, RecipeIngredientUpdateSchema, ErrorResponseSchema
)
from ..utils.exceptions import (
    RecipeNotFoundError, RecipeIngredientNotFoundError, RecipeValidationError,
    CircularDependencyError, MaxDepthExceededError, TooManyIngredientsError
)
from ..models.recipe import RecipeStatus

logger = structlog.get_logger("recipe_service.resources")
blp = Blueprint('recipes', __name__, url_prefix='/api/v1/recipes', description='Recipe operations')


@blp.route('/')
class RecipeCollection(MethodView):
    """Recipe collection endpoints."""
    
    def __init__(self):
        self.repository = RecipeRepository()
    
    @blp.arguments(RecipeListQuerySchema, location='query')
    @blp.response(200, RecipeListSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid query parameters')
    def get(self, query_args):
        """Get list of recipes with pagination and filtering.
        
        Retrieve a paginated list of recipes with optional filtering by status
        or product. Supports pagination with configurable page size.
        """
        logger.info("Fetching recipe list", filters=query_args)
        
        try:
            # Convert string enum to enum instance
            status = None
            if query_args.get('status'):
                status = RecipeStatus(query_args['status'])
            
            # Get recipes from repository
            recipes, pagination_meta = self.repository.get_all(
                page=query_args['page'],
                per_page=query_args['per_page'],
                status=status,
                product_id=query_args.get('product_id'),
                include_relationships=query_args['include_relationships']
            )
            
            # Convert to dict format and add ingredients count
            recipes_data = []
            for recipe in recipes:
                recipe_dict = recipe.to_dict(include_relationships=query_args['include_relationships'])
                recipe_dict['ingredients_count'] = recipe.get_total_ingredients_count()
                recipes_data.append(recipe_dict)
            
            result = {
                'recipes': recipes_data,
                'pagination': pagination_meta
            }
            
            logger.info("Recipe list fetched successfully", count=len(recipes_data))
            return result
            
        except Exception as e:
            logger.error("Error fetching recipe list", error=str(e))
            abort(500, message="Internal server error while fetching recipes")
    
    @blp.arguments(RecipeCreateSchema)
    @blp.response(201, RecipeResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid recipe data')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Recipe validation failed')
    def post(self, recipe_data):
        """Create a new recipe.
        
        Create a new recipe with ingredients. Recipe names must be unique per product.
        Validates that all ingredient products exist in the Product Service.
        """
        logger.info("Creating new recipe", name=recipe_data['name'])
        
        try:
            # TODO: Get user ID from authentication context
            created_by = None  # Will be implemented with authentication
            
            recipe = self.repository.create(recipe_data, created_by)
            
            # Return recipe with relationships
            result = recipe.to_dict(include_relationships=True)
            
            logger.info("Recipe created successfully", recipe_id=str(recipe.id))
            return result, 201
            
        except RecipeValidationError as e:
            logger.warning("Recipe creation failed - validation error", 
                         name=recipe_data['name'], 
                         errors=getattr(e, 'errors', {}))
            abort(400, message=str(e))
        except CircularDependencyError as e:
            logger.warning("Recipe creation failed - circular dependency", name=recipe_data['name'])
            abort(409, message=str(e))
        except TooManyIngredientsError as e:
            logger.warning("Recipe creation failed - too many ingredients", name=recipe_data['name'])
            abort(400, message=str(e))
        except ValidationError as e:
            logger.warning("Recipe creation failed - schema validation", 
                         name=recipe_data['name'], 
                         errors=e.messages)
            abort(400, message="Validation failed", details=e.messages)
        except Exception as e:
            logger.error("Error creating recipe", error=str(e))
            abort(500, message="Internal server error while creating recipe")


@blp.route('/<uuid:recipe_id>')
class RecipeItem(MethodView):
    """Individual recipe endpoints."""
    
    def __init__(self):
        self.repository = RecipeRepository()
    
    @blp.response(200, RecipeResponseSchema)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Recipe not found')
    def get(self, recipe_id):
        """Get a single recipe by ID.
        
        Retrieve detailed information about a specific recipe including
        its ingredients, tags, and nutritional information.
        """
        logger.info("Fetching recipe", recipe_id=str(recipe_id))
        
        try:
            recipe = self.repository.get_by_id(recipe_id, include_relationships=True)
            
            if not recipe:
                logger.warning("Recipe not found", recipe_id=str(recipe_id))
                abort(404, message=f"Recipe with ID {recipe_id} not found")
            
            result = recipe.to_dict(include_relationships=True)
            
            logger.info("Recipe fetched successfully", recipe_id=str(recipe_id))
            return result
            
        except Exception as e:
            logger.error("Error fetching recipe", recipe_id=str(recipe_id), error=str(e))
            abort(500, message="Internal server error while fetching recipe")
    
    @blp.arguments(RecipeUpdateSchema)
    @blp.response(200, RecipeResponseSchema)
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Invalid recipe data')
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Recipe not found')
    @blp.alt_response(409, schema=ErrorResponseSchema, description='Validation failed')
    def put(self, recipe_data, recipe_id):
        """Update a recipe.
        
        Update an existing recipe with the provided data. Only provided fields
        will be updated. Validates circular dependencies and ingredient existence.
        """
        logger.info("Updating recipe", recipe_id=str(recipe_id), data=recipe_data)
        
        try:
            # TODO: Get user ID from authentication context
            updated_by = None  # Will be implemented with authentication
            
            recipe = self.repository.update(recipe_id, recipe_data, updated_by)
            
            # Return updated recipe with relationships
            result = recipe.to_dict(include_relationships=True)
            
            logger.info("Recipe updated successfully", recipe_id=str(recipe_id))
            return result
            
        except RecipeNotFoundError as e:
            logger.warning("Recipe update failed - not found", recipe_id=str(recipe_id))
            abort(404, message=str(e))
        except RecipeValidationError as e:
            logger.warning("Recipe update failed - validation error", 
                         recipe_id=str(recipe_id), 
                         errors=getattr(e, 'errors', {}))
            abort(400, message=str(e))
        except CircularDependencyError as e:
            logger.warning("Recipe update failed - circular dependency", recipe_id=str(recipe_id))
            abort(409, message=str(e))
        except MaxDepthExceededError as e:
            logger.warning("Recipe update failed - max depth exceeded", recipe_id=str(recipe_id))
            abort(400, message=str(e))
        except ValidationError as e:
            logger.warning("Recipe update failed - schema validation", 
                         recipe_id=str(recipe_id), 
                         errors=e.messages)
            abort(400, message="Validation failed", details=e.messages)
        except Exception as e:
            logger.error("Error updating recipe", recipe_id=str(recipe_id), error=str(e))
            abort(500, message="Internal server error while updating recipe")
    
    @blp.response(204)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Recipe not found')
    def delete(self, recipe_id):
        """Delete a recipe.
        
        Permanently delete a recipe. This action cannot be undone.
        All ingredients and version history will also be removed.
        """
        logger.info("Deleting recipe", recipe_id=str(recipe_id))
        
        try:
            success = self.repository.delete(recipe_id)
            
            if not success:
                logger.warning("Recipe deletion failed - not found", recipe_id=str(recipe_id))
                abort(404, message=f"Recipe with ID {recipe_id} not found")
            
            logger.info("Recipe deleted successfully", recipe_id=str(recipe_id))
            return '', 204
            
        except Exception as e:
            logger.error("Error deleting recipe", recipe_id=str(recipe_id), error=str(e))
            abort(500, message="Internal server error while deleting recipe")


@blp.route('/by-product/<uuid:product_id>')
class RecipeByProduct(MethodView):
    """Recipe by product endpoints."""
    
    def __init__(self):
        self.repository = RecipeRepository()
    
    @blp.response(200, RecipeResponseSchema)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Recipe not found')
    def get(self, product_id):
        """Get recipe by product ID.
        
        Retrieve the active recipe for a specific product.
        """
        logger.info("Fetching recipe by product", product_id=str(product_id))
        
        try:
            recipe = self.repository.get_by_product_id(product_id, include_relationships=True)
            
            if not recipe:
                logger.warning("Recipe not found for product", product_id=str(product_id))
                abort(404, message=f"No active recipe found for product {product_id}")
            
            result = recipe.to_dict(include_relationships=True)
            
            logger.info("Recipe fetched by product successfully", 
                       recipe_id=str(recipe.id), 
                       product_id=str(product_id))
            return result
            
        except Exception as e:
            logger.error("Error fetching recipe by product", 
                        product_id=str(product_id), 
                        error=str(e))
            abort(500, message="Internal server error while fetching recipe")


@blp.route('/<uuid:recipe_id>/validate')
class RecipeValidation(MethodView):
    """Recipe validation endpoints."""
    
    def __init__(self):
        self.repository = RecipeRepository()
    
    @blp.response(200, RecipeValidationResponseSchema)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Recipe not found')
    def get(self, recipe_id):
        """Validate a recipe.
        
        Perform comprehensive validation of a recipe including business rules,
        circular dependency checking, and ingredient validation.
        """
        logger.info("Validating recipe", recipe_id=str(recipe_id))
        
        try:
            # Check if recipe exists
            recipe = self.repository.get_by_id(recipe_id)
            if not recipe:
                logger.warning("Recipe validation failed - not found", recipe_id=str(recipe_id))
                abort(404, message=f"Recipe with ID {recipe_id} not found")
            
            # Perform validation
            validation_result = self.repository.validate_recipe(recipe_id)
            validation_result['recipe_id'] = str(recipe_id)
            
            logger.info("Recipe validation completed", 
                       recipe_id=str(recipe_id),
                       is_valid=validation_result['is_valid'],
                       errors_count=len(validation_result['validation_errors']))
            
            return validation_result
            
        except Exception as e:
            logger.error("Error validating recipe", recipe_id=str(recipe_id), error=str(e))
            abort(500, message="Internal server error while validating recipe")


@blp.route('/<uuid:recipe_id>/hierarchy')
class RecipeHierarchy(MethodView):
    """Recipe hierarchy endpoints."""
    
    def __init__(self):
        self.repository = RecipeRepository()
    
    @blp.response(200, RecipeHierarchyResponseSchema)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Recipe not found')
    @blp.alt_response(400, schema=ErrorResponseSchema, description='Hierarchy depth exceeded')
    def get(self, recipe_id):
        """Get recipe hierarchy expansion.
        
        Retrieve the hierarchical expansion of a recipe, showing all nested
        ingredients including those from sub-recipes (semi-products).
        
        Query Parameters:
        - max_depth: Maximum recursion depth (default: 10)
        - include_product_details: Include product information (default: true)
        - target_quantity: Scale ingredients to this quantity
        - target_unit: Unit for target quantity (piece/gram)
        """
        logger.info("Getting recipe hierarchy", recipe_id=str(recipe_id))
        
        try:
            # Get query parameters
            max_depth = int(request.args.get('max_depth', 10))
            include_product_details = request.args.get('include_product_details', 'true').lower() == 'true'
            target_quantity = request.args.get('target_quantity')
            target_unit = request.args.get('target_unit')
            
            # Validate parameters
            if max_depth < 1 or max_depth > 20:
                abort(400, message="max_depth must be between 1 and 20")
            
            # Get base hierarchy
            hierarchy = self.repository.get_recipe_hierarchy(
                recipe_id, 
                max_depth, 
                include_product_details
            )
            
            # Apply quantity scaling if requested
            if target_quantity is not None:
                try:
                    target_qty = float(target_quantity)
                    if target_qty <= 0:
                        abort(400, message="target_quantity must be positive")
                    
                    # Get recipe for scaling calculation
                    recipe = self.repository.get_by_id(recipe_id)
                    if recipe and recipe.yield_quantity:
                        scale_factor = target_qty / float(recipe.yield_quantity)
                        
                        # Scale all quantities in hierarchy
                        for item in hierarchy:
                            item['quantity'] = round(float(item['quantity']) * scale_factor, 3)
                            item['scaled_for_quantity'] = target_qty
                            item['scaled_for_unit'] = target_unit or recipe.yield_unit.value if recipe.yield_unit else None
                            item['scale_factor'] = scale_factor
                    else:
                        abort(400, message="Recipe must have yield_quantity for scaling")
                        
                except ValueError:
                    abort(400, message="target_quantity must be a valid number")
            
            # Calculate maximum actual depth
            max_actual_depth = max([item['depth_level'] for item in hierarchy], default=0)
            
            # Group by depth level for better organization
            hierarchy_by_depth = {}
            for item in hierarchy:
                depth = item['depth_level']
                if depth not in hierarchy_by_depth:
                    hierarchy_by_depth[depth] = []
                hierarchy_by_depth[depth].append(item)
            
            result = {
                'recipe_id': str(recipe_id),
                'hierarchy': hierarchy,
                'hierarchy_by_depth': hierarchy_by_depth,
                'max_depth': max_actual_depth,
                'total_items': len(hierarchy),
                'scaling_applied': target_quantity is not None,
                'parameters': {
                    'max_depth': max_depth,
                    'include_product_details': include_product_details,
                    'target_quantity': float(target_quantity) if target_quantity else None,
                    'target_unit': target_unit
                }
            }
            
            logger.info("Recipe hierarchy retrieved successfully", 
                       recipe_id=str(recipe_id),
                       hierarchy_items=len(hierarchy),
                       max_depth=max_actual_depth,
                       scaling_applied=target_quantity is not None)
            
            return result
            
        except RecipeNotFoundError as e:
            logger.warning("Recipe hierarchy failed - not found", recipe_id=str(recipe_id))
            abort(404, message=str(e))
        except MaxDepthExceededError as e:
            logger.warning("Recipe hierarchy failed - depth exceeded", recipe_id=str(recipe_id))
            abort(400, message=str(e))
        except ValueError as e:
            logger.warning("Recipe hierarchy failed - invalid parameter", recipe_id=str(recipe_id))
            abort(400, message="Invalid query parameter")
        except Exception as e:
            logger.error("Error getting recipe hierarchy", recipe_id=str(recipe_id), error=str(e))
            abort(500, message="Internal server error while getting recipe hierarchy")


@blp.route('/<uuid:recipe_id>/ingredients/<uuid:ingredient_id>')
class RecipeIngredientItem(MethodView):
    """Individual recipe ingredient endpoints."""
    
    def __init__(self):
        self.repository = RecipeIngredientRepository()
    
    @blp.arguments(RecipeIngredientUpdateSchema)
    @blp.response(200, schema={'type': 'object'})
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Ingredient not found')
    def put(self, ingredient_data, recipe_id, ingredient_id):
        """Update a recipe ingredient.
        
        Update an individual ingredient within a recipe.
        """
        logger.info("Updating recipe ingredient", 
                   recipe_id=str(recipe_id), 
                   ingredient_id=str(ingredient_id))
        
        try:
            ingredient = self.repository.update(ingredient_id, ingredient_data)
            
            result = ingredient.to_dict()
            
            logger.info("Recipe ingredient updated successfully", 
                       ingredient_id=str(ingredient_id))
            return result
            
        except RecipeIngredientNotFoundError as e:
            logger.warning("Recipe ingredient update failed - not found", 
                         ingredient_id=str(ingredient_id))
            abort(404, message=str(e))
        except ValidationError as e:
            logger.warning("Recipe ingredient update failed - validation error", 
                         ingredient_id=str(ingredient_id), 
                         errors=e.messages)
            abort(400, message="Validation failed", details=e.messages)
        except Exception as e:
            logger.error("Error updating recipe ingredient", 
                        ingredient_id=str(ingredient_id), 
                        error=str(e))
            abort(500, message="Internal server error while updating ingredient")
    
    @blp.response(204)
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Ingredient not found')
    def delete(self, recipe_id, ingredient_id):
        """Delete a recipe ingredient.
        
        Remove an ingredient from a recipe.
        """
        logger.info("Deleting recipe ingredient", 
                   recipe_id=str(recipe_id), 
                   ingredient_id=str(ingredient_id))
        
        try:
            success = self.repository.delete(ingredient_id)
            
            if not success:
                logger.warning("Recipe ingredient deletion failed - not found", 
                             ingredient_id=str(ingredient_id))
                abort(404, message=f"Ingredient with ID {ingredient_id} not found")
            
            logger.info("Recipe ingredient deleted successfully", 
                       ingredient_id=str(ingredient_id))
            return '', 204
            
        except Exception as e:
            logger.error("Error deleting recipe ingredient", 
                        ingredient_id=str(ingredient_id), 
                        error=str(e))
            abort(500, message="Internal server error while deleting ingredient")


@blp.route('/tags')
class RecipeTagCollection(MethodView):
    """Recipe tag collection endpoints."""
    
    def __init__(self):
        self.repository = RecipeTagRepository()
    
    @blp.response(200, schema={'type': 'array', 'items': {'$ref': '#/components/schemas/RecipeTag'}})
    def get(self):
        """Get all recipe tags.
        
        Retrieve a list of all available recipe tags.
        """
        logger.info("Fetching all recipe tags")
        
        try:
            tags = self.repository.get_all()
            result = [tag.to_dict() for tag in tags]
            
            logger.info("Recipe tags fetched successfully", count=len(result))
            return result
            
        except Exception as e:
            logger.error("Error fetching recipe tags", error=str(e))
            abort(500, message="Internal server error while fetching tags")


@blp.route('/<uuid:recipe_id>/analysis')
class RecipeAnalysis(MethodView):
    """Recipe analysis endpoints."""
    
    def __init__(self):
        self.repository = RecipeRepository()
    
    @blp.response(200, schema={'type': 'object'})
    @blp.alt_response(404, schema=ErrorResponseSchema, description='Recipe not found')
    def get(self, recipe_id):
        """Get comprehensive recipe analysis.
        
        Provides detailed analysis including complexity metrics, dependency analysis,
        and hierarchical structure information for recipe optimization.
        """
        logger.info("Analyzing recipe", recipe_id=str(recipe_id))
        
        try:
            # Check if recipe exists
            recipe = self.repository.get_by_id(recipe_id)
            if not recipe:
                logger.warning("Recipe analysis failed - not found", recipe_id=str(recipe_id))
                abort(404, message=f"Recipe with ID {recipe_id} not found")
            
            # Get complexity metrics
            complexity = self.repository.get_recipe_complexity_metrics(recipe_id)
            
            # Get dependencies
            dependencies = self.repository.get_recipe_dependencies(recipe_id)
            
            # Get hierarchy for analysis
            hierarchy = self.repository.get_recipe_hierarchy(recipe_id, max_depth=20, include_product_details=True)
            
            # Analyze ingredient distribution by unit
            unit_distribution = {}
            for item in hierarchy:
                unit = item['unit']
                if unit not in unit_distribution:
                    unit_distribution[unit] = {'count': 0, 'total_quantity': 0}
                unit_distribution[unit]['count'] += 1
                unit_distribution[unit]['total_quantity'] += float(item['quantity'])
            
            # Analyze depth distribution
            depth_distribution = {}
            for item in hierarchy:
                depth = item['depth_level']
                if depth not in depth_distribution:
                    depth_distribution[depth] = 0
                depth_distribution[depth] += 1
            
            # Performance insights
            performance_insights = []
            
            if complexity['hierarchy_depth'] > 5:
                performance_insights.append({
                    'type': 'warning',
                    'message': 'Deep hierarchy may impact calculation performance',
                    'recommendation': 'Consider flattening some sub-recipes'
                })
            
            if complexity['ingredient_count'] > 20:
                performance_insights.append({
                    'type': 'info',
                    'message': 'Large number of direct ingredients',
                    'recommendation': 'Consider grouping ingredients logically'
                })
            
            if len(hierarchy) > 50:
                performance_insights.append({
                    'type': 'warning',
                    'message': 'Large expanded ingredient count may slow calculations',
                    'recommendation': 'Review recipe structure for optimization'
                })
            
            result = {
                'recipe_id': str(recipe_id),
                'complexity_metrics': complexity,
                'dependencies': dependencies,
                'hierarchy_analysis': {
                    'total_expanded_ingredients': len(hierarchy),
                    'unit_distribution': unit_distribution,
                    'depth_distribution': depth_distribution
                },
                'performance_insights': performance_insights,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("Recipe analysis completed", 
                       recipe_id=str(recipe_id),
                       complexity_level=complexity['complexity_level'],
                       total_ingredients=len(hierarchy))
            
            return result
            
        except Exception as e:
            logger.error("Error analyzing recipe", recipe_id=str(recipe_id), error=str(e))
            abort(500, message="Internal server error while analyzing recipe")


@blp.route('/product/<uuid:product_id>')  
class RecipesByProduct(MethodView):
    """Recipes by product endpoints."""
    
    def __init__(self):
        self.repository = RecipeRepository()
    
    @blp.response(200, schema={'type': 'object'})
    @blp.alt_response(404, schema=ErrorResponseSchema, description='No recipes found')
    def get(self, product_id):
        """Get all recipes that use a specific product as ingredient.
        
        Retrieve all recipes where the specified product is used as an ingredient,
        useful for impact analysis when modifying products.
        """
        logger.info("Finding recipes using product", product_id=str(product_id))
        
        try:
            recipes = self.repository.get_recipes_using_product(product_id)
            
            if not recipes:
                logger.info("No recipes found using product", product_id=str(product_id))
                return {
                    'product_id': str(product_id),
                    'recipes': [],
                    'total_count': 0
                }
            
            # Convert to response format
            recipes_data = []
            for recipe in recipes:
                recipe_dict = recipe.to_dict(include_relationships=False)
                # Add usage details
                ingredient = None
                for ing in recipe.ingredients:
                    if str(ing.ingredient_product_id) == str(product_id):
                        ingredient = ing
                        break
                
                if ingredient:
                    recipe_dict['usage_details'] = {
                        'quantity': float(ingredient.quantity),
                        'unit': ingredient.unit.value,
                        'is_optional': ingredient.is_optional,
                        'ingredient_group': ingredient.ingredient_group,
                        'notes': ingredient.notes
                    }
                
                recipes_data.append(recipe_dict)
            
            result = {
                'product_id': str(product_id),
                'recipes': recipes_data,
                'total_count': len(recipes_data)
            }
            
            logger.info("Recipes using product found", 
                       product_id=str(product_id),
                       recipe_count=len(recipes_data))
            
            return result
            
        except Exception as e:
            logger.error("Error finding recipes using product", 
                        product_id=str(product_id), 
                        error=str(e))
            abort(500, message="Internal server error while finding recipes")