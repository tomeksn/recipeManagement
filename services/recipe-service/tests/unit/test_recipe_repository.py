"""Unit tests for Recipe repository."""
import pytest
import uuid
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.recipe_repository import RecipeRepository, RecipeIngredientRepository, RecipeTagRepository
from app.models.recipe import Recipe, RecipeIngredient, RecipeTag, RecipeStatus, IngredientUnit
from app.extensions import db
from app.utils.exceptions import (
    RecipeNotFoundError, RecipeValidationError, CircularDependencyError,
    MaxDepthExceededError, TooManyIngredientsError
)


class TestRecipeRepository:
    """Test cases for RecipeRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return RecipeRepository()
    
    @pytest.fixture
    def sample_recipe_data(self):
        """Sample recipe data for testing."""
        return {
            'product_id': str(uuid.uuid4()),
            'name': 'Test Recipe',
            'description': 'A test recipe',
            'status': 'draft',
            'yield_quantity': 500.0,
            'yield_unit': 'gram',
            'preparation_time': 30,
            'ingredients': [
                {
                    'ingredient_product_id': str(uuid.uuid4()),
                    'quantity': 100.0,
                    'unit': 'gram',
                    'sort_order': 1
                },
                {
                    'ingredient_product_id': str(uuid.uuid4()),
                    'quantity': 2,
                    'unit': 'piece',
                    'sort_order': 2
                }
            ]
        }
    
    def test_get_by_id_found(self, app, repository):
        """Test getting recipe by ID when recipe exists."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.commit()
            
            # Test repository method
            found_recipe = repository.get_by_id(recipe.id)
            
            assert found_recipe is not None
            assert found_recipe.id == recipe.id
            assert found_recipe.name == "Test Recipe"
    
    def test_get_by_id_not_found(self, app, repository):
        """Test getting recipe by ID when recipe doesn't exist."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            found_recipe = repository.get_by_id(fake_id)
            
            assert found_recipe is None
    
    def test_get_by_product_id_found(self, app, repository):
        """Test getting recipe by product ID when recipe exists."""
        with app.app_context():
            db.create_all()
            
            product_id = uuid.uuid4()
            recipe = Recipe(
                product_id=product_id,
                name="Product Recipe",
                status=RecipeStatus.ACTIVE
            )
            db.session.add(recipe)
            db.session.commit()
            
            found_recipe = repository.get_by_product_id(product_id)
            
            assert found_recipe is not None
            assert found_recipe.product_id == product_id
            assert found_recipe.status == RecipeStatus.ACTIVE
    
    def test_get_by_product_id_only_active(self, app, repository):
        """Test that get_by_product_id only returns active recipes."""
        with app.app_context():
            db.create_all()
            
            product_id = uuid.uuid4()
            
            # Create draft recipe (should not be returned)
            draft_recipe = Recipe(
                product_id=product_id,
                name="Draft Recipe",
                status=RecipeStatus.DRAFT
            )
            
            # Create active recipe (should be returned)
            active_recipe = Recipe(
                product_id=product_id,
                name="Active Recipe",
                status=RecipeStatus.ACTIVE
            )
            
            db.session.add_all([draft_recipe, active_recipe])
            db.session.commit()
            
            found_recipe = repository.get_by_product_id(product_id)
            
            assert found_recipe is not None
            assert found_recipe.id == active_recipe.id
            assert found_recipe.status == RecipeStatus.ACTIVE
    
    def test_get_all_with_pagination(self, app, repository):
        """Test getting all recipes with pagination."""
        with app.app_context():
            db.create_all()
            
            # Create test recipes
            for i in range(5):
                recipe = Recipe(
                    product_id=uuid.uuid4(),
                    name=f"Recipe {i}",
                    status=RecipeStatus.ACTIVE
                )
                db.session.add(recipe)
            
            db.session.commit()
            
            # Test pagination
            recipes, pagination = repository.get_all(page=1, per_page=3)
            
            assert len(recipes) == 3
            assert pagination['total'] == 5
            assert pagination['pages'] == 2
            assert pagination['page'] == 1
            assert pagination['per_page'] == 3
            assert pagination['has_next'] is True
            assert pagination['has_prev'] is False
    
    def test_get_all_with_status_filter(self, app, repository):
        """Test getting recipes with status filter."""
        with app.app_context():
            db.create_all()
            
            # Create recipes with different statuses
            active_recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Active Recipe",
                status=RecipeStatus.ACTIVE
            )
            
            draft_recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Draft Recipe",
                status=RecipeStatus.DRAFT
            )
            
            db.session.add_all([active_recipe, draft_recipe])
            db.session.commit()
            
            # Test filtering by status
            recipes, pagination = repository.get_all(status=RecipeStatus.ACTIVE)
            
            assert len(recipes) == 1
            assert recipes[0].status == RecipeStatus.ACTIVE
            assert pagination['total'] == 1
    
    @patch('app.services.recipe_repository.product_client')
    def test_create_recipe_success(self, mock_product_client, app, repository, sample_recipe_data):
        """Test creating a recipe successfully."""
        with app.app_context():
            db.create_all()
            
            # Mock product client
            mock_product_client.validate_product_exists.return_value = True
            mock_product_client.validate_products_exist.return_value = {
                sample_recipe_data['ingredients'][0]['ingredient_product_id']: True,
                sample_recipe_data['ingredients'][1]['ingredient_product_id']: True
            }
            
            # Create recipe
            recipe = repository.create(sample_recipe_data)
            
            assert recipe is not None
            assert recipe.name == "Test Recipe"
            assert recipe.status == RecipeStatus.DRAFT
            assert len(recipe.ingredients) == 2
            assert recipe.version == 1
    
    @patch('app.services.recipe_repository.product_client')
    def test_create_recipe_invalid_product(self, mock_product_client, app, repository, sample_recipe_data):
        """Test creating a recipe with invalid product ID."""
        with app.app_context():
            db.create_all()
            
            # Mock product client to return False
            mock_product_client.validate_product_exists.return_value = False
            
            with pytest.raises(RecipeValidationError):
                repository.create(sample_recipe_data)
    
    @patch('app.services.recipe_repository.product_client')
    def test_create_recipe_invalid_ingredients(self, mock_product_client, app, repository, sample_recipe_data):
        """Test creating a recipe with invalid ingredient products."""
        with app.app_context():
            db.create_all()
            
            # Mock product client
            mock_product_client.validate_product_exists.return_value = True
            mock_product_client.validate_products_exist.return_value = {
                sample_recipe_data['ingredients'][0]['ingredient_product_id']: False,  # Invalid
                sample_recipe_data['ingredients'][1]['ingredient_product_id']: True
            }
            
            with pytest.raises(RecipeValidationError):
                repository.create(sample_recipe_data)
    
    @patch('app.services.recipe_repository.product_client')
    @patch('app.services.recipe_repository.current_app')
    def test_create_recipe_too_many_ingredients(self, mock_app, mock_product_client, app, repository, sample_recipe_data):
        """Test creating a recipe with too many ingredients."""
        with app.app_context():
            db.create_all()
            
            # Mock config
            mock_app.config = {'MAX_INGREDIENTS_PER_RECIPE': 1}
            
            # Mock product client
            mock_product_client.validate_product_exists.return_value = True
            
            with pytest.raises(TooManyIngredientsError):
                repository.create(sample_recipe_data)  # Has 2 ingredients, max is 1
    
    def test_update_recipe_success(self, app, repository):
        """Test updating a recipe successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Original Name",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.commit()
            
            # Update recipe
            update_data = {
                'name': 'Updated Name',
                'description': 'Updated description',
                'status': 'active'
            }
            
            updated_recipe = repository.update(recipe.id, update_data)
            
            assert updated_recipe.name == "Updated Name"
            assert updated_recipe.description == "Updated description"
            assert updated_recipe.status == RecipeStatus.ACTIVE
    
    def test_update_recipe_not_found(self, app, repository):
        """Test updating a non-existent recipe."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            update_data = {'name': 'Updated Name'}
            
            with pytest.raises(RecipeNotFoundError):
                repository.update(fake_id, update_data)
    
    def test_delete_recipe_success(self, app, repository):
        """Test deleting a recipe successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="To Delete",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.commit()
            recipe_id = recipe.id
            
            # Delete recipe
            success = repository.delete(recipe_id)
            
            assert success is True
            
            # Verify deletion
            deleted_recipe = repository.get_by_id(recipe_id)
            assert deleted_recipe is None
    
    def test_delete_recipe_not_found(self, app, repository):
        """Test deleting a non-existent recipe."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            success = repository.delete(fake_id)
            
            assert success is False
    
    @patch('app.services.recipe_repository.product_client')
    def test_get_recipe_hierarchy(self, mock_product_client, app, repository):
        """Test getting recipe hierarchy."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.ACTIVE
            )
            db.session.add(recipe)
            db.session.commit()
            
            # Mock product client
            mock_product_client.get_products_batch.return_value = {}
            
            # Mock database function result
            with patch.object(repository.session, 'execute') as mock_execute:
                mock_result = Mock()
                mock_result.__iter__ = Mock(return_value=iter([]))
                mock_execute.return_value = mock_result
                
                hierarchy = repository.get_recipe_hierarchy(recipe.id)
                
                assert hierarchy == []
    
    def test_get_recipe_hierarchy_not_found(self, app, repository):
        """Test getting hierarchy for non-existent recipe."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            
            with pytest.raises(RecipeNotFoundError):
                repository.get_recipe_hierarchy(fake_id)
    
    def test_validate_recipe(self, app, repository):
        """Test recipe validation."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.commit()
            
            # Mock database function result
            with patch.object(repository.session, 'execute') as mock_execute:
                mock_result = Mock()
                mock_result.is_valid = True
                mock_result.validation_errors = []
                mock_execute.return_value.first.return_value = mock_result
                
                validation_result = repository.validate_recipe(recipe.id)
                
                assert validation_result['is_valid'] is True
                assert validation_result['validation_errors'] == []
    
    def test_get_recipe_dependencies(self, app, repository):
        """Test getting recipe dependencies."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.commit()
            
            dependencies = repository.get_recipe_dependencies(recipe.id)
            
            assert dependencies == []  # No dependencies created
    
    def test_get_recipes_using_product(self, app, repository):
        """Test getting recipes that use a specific product."""
        with app.app_context():
            db.create_all()
            
            product_id = uuid.uuid4()
            
            # Create recipe with ingredient
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.ACTIVE
            )
            db.session.add(recipe)
            db.session.flush()
            
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=product_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            db.session.add(ingredient)
            db.session.commit()
            
            recipes = repository.get_recipes_using_product(product_id)
            
            assert len(recipes) == 1
            assert recipes[0].id == recipe.id
    
    def test_get_recipe_complexity_metrics(self, app, repository):
        """Test getting recipe complexity metrics."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe with ingredients
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.ACTIVE
            )
            db.session.add(recipe)
            db.session.flush()
            
            # Add ingredients
            for i in range(3):
                ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_product_id=uuid.uuid4(),
                    quantity=Decimal('100.0'),
                    unit=IngredientUnit.GRAM,
                    is_optional=(i == 2)  # Last ingredient is optional
                )
                db.session.add(ingredient)
            
            db.session.commit()
            
            # Mock hierarchy function
            with patch.object(repository, 'get_recipe_hierarchy') as mock_hierarchy:
                mock_hierarchy.return_value = [
                    {'depth_level': 1}, {'depth_level': 1}, {'depth_level': 2}
                ]
                
                metrics = repository.get_recipe_complexity_metrics(recipe.id)
                
                assert metrics['ingredient_count'] == 3
                assert metrics['hierarchy_depth'] == 2
                assert metrics['total_ingredients_expanded'] == 3
                assert metrics['optional_ingredients'] == 1
                assert metrics['required_ingredients'] == 2
                assert 'complexity_score' in metrics
                assert 'complexity_level' in metrics


class TestRecipeIngredientRepository:
    """Test cases for RecipeIngredientRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return RecipeIngredientRepository()
    
    def test_get_by_id(self, app, repository):
        """Test getting ingredient by ID."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe and ingredient
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            db.session.add(ingredient)
            db.session.commit()
            
            found_ingredient = repository.get_by_id(ingredient.id)
            
            assert found_ingredient is not None
            assert found_ingredient.id == ingredient.id
    
    def test_get_by_recipe(self, app, repository):
        """Test getting ingredients by recipe ID."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            # Add ingredients with different sort orders
            ingredient1 = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM,
                sort_order=2
            )
            
            ingredient2 = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('50.0'),
                unit=IngredientUnit.GRAM,
                sort_order=1
            )
            
            db.session.add_all([ingredient1, ingredient2])
            db.session.commit()
            
            ingredients = repository.get_by_recipe(recipe.id)
            
            assert len(ingredients) == 2
            # Should be sorted by sort_order
            assert ingredients[0].sort_order == 1
            assert ingredients[1].sort_order == 2
    
    def test_update_ingredient(self, app, repository):
        """Test updating an ingredient."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe and ingredient
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM,
                notes="Original notes"
            )
            db.session.add(ingredient)
            db.session.commit()
            
            # Update ingredient
            update_data = {
                'quantity': 200.0,
                'notes': 'Updated notes',
                'is_optional': True
            }
            
            updated_ingredient = repository.update(ingredient.id, update_data)
            
            assert updated_ingredient.quantity == Decimal('200.0')
            assert updated_ingredient.notes == 'Updated notes'
            assert updated_ingredient.is_optional is True
    
    def test_delete_ingredient(self, app, repository):
        """Test deleting an ingredient."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe and ingredient
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            db.session.add(ingredient)
            db.session.commit()
            ingredient_id = ingredient.id
            
            # Delete ingredient
            success = repository.delete(ingredient_id)
            
            assert success is True
            
            # Verify deletion
            deleted_ingredient = repository.get_by_id(ingredient_id)
            assert deleted_ingredient is None


class TestRecipeTagRepository:
    """Test cases for RecipeTagRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return RecipeTagRepository()
    
    def test_get_all_tags(self, app, repository):
        """Test getting all tags."""
        with app.app_context():
            db.create_all()
            
            # Create test tags
            tag1 = RecipeTag(name="dessert")
            tag2 = RecipeTag(name="appetizer")
            tag3 = RecipeTag(name="breakfast")
            
            db.session.add_all([tag1, tag2, tag3])
            db.session.commit()
            
            tags = repository.get_all()
            
            assert len(tags) == 3
            # Should be ordered by name
            tag_names = [tag.name for tag in tags]
            assert tag_names == sorted(tag_names)
    
    def test_get_tag_by_id(self, app, repository):
        """Test getting tag by ID."""
        with app.app_context():
            db.create_all()
            
            tag = RecipeTag(name="test_tag")
            db.session.add(tag)
            db.session.commit()
            
            found_tag = repository.get_by_id(tag.id)
            
            assert found_tag is not None
            assert found_tag.id == tag.id
            assert found_tag.name == "test_tag"
    
    def test_create_tag(self, app, repository):
        """Test creating a new tag."""
        with app.app_context():
            db.create_all()
            
            tag_data = {
                'name': 'new_tag',
                'color': '#FF0000',
                'description': 'A new tag'
            }
            
            created_tag = repository.create(tag_data)
            
            assert created_tag is not None
            assert created_tag.name == 'new_tag'
            assert created_tag.color == '#FF0000'
            assert created_tag.description == 'A new tag'