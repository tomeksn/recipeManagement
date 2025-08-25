"""Unit tests for Recipe models."""
import pytest
import uuid
from datetime import datetime
from decimal import Decimal

from app.models.recipe import (
    Recipe, RecipeIngredient, RecipeVersion, RecipeDependency, 
    RecipeNutrition, RecipeTag, RecipeAudit,
    RecipeStatus, IngredientUnit
)
from app.extensions import db


class TestRecipeModel:
    """Test cases for Recipe model."""
    
    def test_create_recipe_with_required_fields(self, app):
        """Test creating recipe with required fields only."""
        with app.app_context():
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe"
            )
            
            assert recipe.product_id is not None
            assert recipe.name == "Test Recipe"
            assert recipe.status == RecipeStatus.DRAFT
            assert recipe.version == 1
            assert recipe.id is not None
    
    def test_create_recipe_with_all_fields(self, app):
        """Test creating recipe with all fields."""
        with app.app_context():
            recipe_id = uuid.uuid4()
            product_id = uuid.uuid4()
            user_id = uuid.uuid4()
            
            recipe = Recipe(
                id=recipe_id,
                product_id=product_id,
                name="Complete Recipe",
                description="A complete recipe description",
                version=2,
                status=RecipeStatus.ACTIVE,
                yield_quantity=Decimal('500.0'),
                yield_unit=IngredientUnit.GRAM,
                preparation_time=30,
                notes="Recipe notes",
                created_by=user_id,
                updated_by=user_id
            )
            
            assert recipe.id == recipe_id
            assert recipe.product_id == product_id
            assert recipe.name == "Complete Recipe"
            assert recipe.description == "A complete recipe description"
            assert recipe.version == 2
            assert recipe.status == RecipeStatus.ACTIVE
            assert recipe.yield_quantity == Decimal('500.0')
            assert recipe.yield_unit == IngredientUnit.GRAM
            assert recipe.preparation_time == 30
            assert recipe.notes == "Recipe notes"
            assert recipe.created_by == user_id
            assert recipe.updated_by == user_id
    
    def test_recipe_name_validation(self, app):
        """Test recipe name validation."""
        with app.app_context():
            # Test empty name
            with pytest.raises(ValueError, match="Recipe name cannot be empty"):
                Recipe(product_id=uuid.uuid4(), name="")
            
            # Test whitespace-only name
            with pytest.raises(ValueError, match="Recipe name cannot be empty"):
                Recipe(product_id=uuid.uuid4(), name="   ")
            
            # Test name trimming
            recipe = Recipe(product_id=uuid.uuid4(), name="  Test Recipe  ")
            assert recipe.name == "Test Recipe"
    
    def test_recipe_version_validation(self, app):
        """Test recipe version validation."""
        with app.app_context():
            # Test negative version
            with pytest.raises(ValueError, match="Recipe version must be positive"):
                Recipe(product_id=uuid.uuid4(), name="Test", version=0)
            
            with pytest.raises(ValueError, match="Recipe version must be positive"):
                Recipe(product_id=uuid.uuid4(), name="Test", version=-1)
    
    def test_recipe_yield_quantity_validation(self, app):
        """Test recipe yield quantity validation."""
        with app.app_context():
            # Test negative yield quantity
            with pytest.raises(ValueError, match="Yield quantity must be positive"):
                Recipe(product_id=uuid.uuid4(), name="Test", yield_quantity=Decimal('-1.0'))
            
            with pytest.raises(ValueError, match="Yield quantity must be positive"):
                Recipe(product_id=uuid.uuid4(), name="Test", yield_quantity=Decimal('0.0'))
    
    def test_recipe_preparation_time_validation(self, app):
        """Test recipe preparation time validation."""
        with app.app_context():
            # Test negative preparation time
            with pytest.raises(ValueError, match="Preparation time must be positive"):
                Recipe(product_id=uuid.uuid4(), name="Test", preparation_time=-1)
            
            with pytest.raises(ValueError, match="Preparation time must be positive"):
                Recipe(product_id=uuid.uuid4(), name="Test", preparation_time=0)
    
    def test_recipe_to_dict(self, app):
        """Test recipe to_dict method."""
        with app.app_context():
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                description="Test description",
                status=RecipeStatus.ACTIVE,
                version=2,
                yield_quantity=Decimal('500.0'),
                yield_unit=IngredientUnit.GRAM,
                preparation_time=30
            )
            
            result = recipe.to_dict()
            
            assert result['name'] == "Test Recipe"
            assert result['description'] == "Test description"
            assert result['status'] == "active"
            assert result['version'] == 2
            assert result['yield_quantity'] == 500.0
            assert result['yield_unit'] == "gram"
            assert result['preparation_time'] == 30
            assert 'id' in result
            assert 'product_id' in result
    
    def test_recipe_repr(self, app):
        """Test recipe string representation."""
        with app.app_context():
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                version=2,
                status=RecipeStatus.ACTIVE
            )
            assert repr(recipe) == "<Recipe Test Recipe v2 (active)>"


class TestRecipeIngredientModel:
    """Test cases for RecipeIngredient model."""
    
    def test_create_ingredient_with_required_fields(self, app):
        """Test creating ingredient with required fields only."""
        with app.app_context():
            ingredient = RecipeIngredient(
                recipe_id=uuid.uuid4(),
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            
            assert ingredient.recipe_id is not None
            assert ingredient.ingredient_product_id is not None
            assert ingredient.quantity == Decimal('100.0')
            assert ingredient.unit == IngredientUnit.GRAM
            assert ingredient.sort_order == 0
            assert ingredient.is_optional is False
    
    def test_create_ingredient_with_all_fields(self, app):
        """Test creating ingredient with all fields."""
        with app.app_context():
            ingredient = RecipeIngredient(
                recipe_id=uuid.uuid4(),
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('250.5'),
                unit=IngredientUnit.GRAM,
                sort_order=5,
                ingredient_group="Base",
                notes="Ingredient notes",
                is_optional=True,
                substitute_ingredients=['alt1', 'alt2']
            )
            
            assert ingredient.quantity == Decimal('250.5')
            assert ingredient.unit == IngredientUnit.GRAM
            assert ingredient.sort_order == 5
            assert ingredient.ingredient_group == "Base"
            assert ingredient.notes == "Ingredient notes"
            assert ingredient.is_optional is True
            assert ingredient.substitute_ingredients == ['alt1', 'alt2']
    
    def test_ingredient_quantity_validation(self, app):
        """Test ingredient quantity validation."""
        with app.app_context():
            # Test negative quantity
            with pytest.raises(ValueError, match="Ingredient quantity must be positive"):
                RecipeIngredient(
                    recipe_id=uuid.uuid4(),
                    ingredient_product_id=uuid.uuid4(),
                    quantity=Decimal('-1.0'),
                    unit=IngredientUnit.GRAM
                )
            
            # Test zero quantity
            with pytest.raises(ValueError, match="Ingredient quantity must be positive"):
                RecipeIngredient(
                    recipe_id=uuid.uuid4(),
                    ingredient_product_id=uuid.uuid4(),
                    quantity=Decimal('0.0'),
                    unit=IngredientUnit.GRAM
                )
    
    def test_ingredient_sort_order_validation(self, app):
        """Test ingredient sort order validation."""
        with app.app_context():
            # Test negative sort order
            with pytest.raises(ValueError, match="Sort order must be non-negative"):
                RecipeIngredient(
                    recipe_id=uuid.uuid4(),
                    ingredient_product_id=uuid.uuid4(),
                    quantity=Decimal('100.0'),
                    unit=IngredientUnit.GRAM,
                    sort_order=-1
                )
    
    def test_ingredient_to_dict(self, app):
        """Test ingredient to_dict method."""
        with app.app_context():
            ingredient = RecipeIngredient(
                recipe_id=uuid.uuid4(),
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM,
                sort_order=1,
                ingredient_group="Base",
                is_optional=True
            )
            
            result = ingredient.to_dict()
            
            assert result['quantity'] == 100.0
            assert result['unit'] == "gram"
            assert result['sort_order'] == 1
            assert result['ingredient_group'] == "Base"
            assert result['is_optional'] is True
            assert 'id' in result
            assert 'recipe_id' in result
            assert 'ingredient_product_id' in result


class TestRecipeTagModel:
    """Test cases for RecipeTag model."""
    
    def test_create_tag_with_required_fields(self, app):
        """Test creating tag with required fields only."""
        with app.app_context():
            tag = RecipeTag(name="test-tag")
            
            assert tag.name == "test-tag"
            assert tag.color is None
            assert tag.description is None
            assert tag.id is not None
    
    def test_create_tag_with_all_fields(self, app):
        """Test creating tag with all fields."""
        with app.app_context():
            tag = RecipeTag(
                name="complete-tag",
                color="#FF0000",
                description="A complete tag description"
            )
            
            assert tag.name == "complete-tag"
            assert tag.color == "#FF0000"
            assert tag.description == "A complete tag description"
    
    def test_tag_name_validation(self, app):
        """Test tag name validation."""
        with app.app_context():
            # Test empty name
            with pytest.raises(ValueError, match="Tag name cannot be empty"):
                RecipeTag(name="")
            
            # Test name trimming
            tag = RecipeTag(name="  test-tag  ")
            assert tag.name == "test-tag"
    
    def test_tag_color_validation(self, app):
        """Test tag color validation."""
        with app.app_context():
            # Test valid color
            tag = RecipeTag(name="test", color="#FF0000")
            assert tag.color == "#FF0000"
            
            # Test invalid color format
            with pytest.raises(ValueError, match="Color must be a valid hex color code"):
                RecipeTag(name="test", color="red")
            
            with pytest.raises(ValueError, match="Color must be a valid hex color code"):
                RecipeTag(name="test", color="#FF")
    
    def test_tag_to_dict(self, app):
        """Test tag to_dict method."""
        with app.app_context():
            tag = RecipeTag(
                name="test-tag",
                color="#FF0000",
                description="Test description"
            )
            
            result = tag.to_dict()
            
            assert result['name'] == "test-tag"
            assert result['color'] == "#FF0000"
            assert result['description'] == "Test description"
            assert 'id' in result
            assert 'created_at' in result


class TestRecipeNutritionModel:
    """Test cases for RecipeNutrition model."""
    
    def test_create_nutrition(self, app):
        """Test creating nutrition information."""
        with app.app_context():
            nutrition = RecipeNutrition(
                recipe_id=uuid.uuid4(),
                calories=Decimal('250.5'),
                protein=Decimal('12.0'),
                carbohydrates=Decimal('30.0'),
                fat=Decimal('8.5'),
                calculation_method='manual'
            )
            
            assert nutrition.calories == Decimal('250.5')
            assert nutrition.protein == Decimal('12.0')
            assert nutrition.carbohydrates == Decimal('30.0')
            assert nutrition.fat == Decimal('8.5')
            assert nutrition.calculation_method == 'manual'
    
    def test_nutrition_to_dict(self, app):
        """Test nutrition to_dict method."""
        with app.app_context():
            nutrition = RecipeNutrition(
                recipe_id=uuid.uuid4(),
                calories=Decimal('250.5'),
                protein=Decimal('12.0'),
                calculation_method='automated'
            )
            
            result = nutrition.to_dict()
            
            assert result['calories'] == 250.5
            assert result['protein'] == 12.0
            assert result['calculation_method'] == 'automated'
            assert 'recipe_id' in result
            assert 'calculated_at' in result


class TestRecipeVersionModel:
    """Test cases for RecipeVersion model."""
    
    def test_create_version(self, app):
        """Test creating recipe version."""
        with app.app_context():
            version = RecipeVersion(
                recipe_id=uuid.uuid4(),
                version_number=2,
                recipe_data={'name': 'Test Recipe'},
                change_summary='Updated ingredients'
            )
            
            assert version.version_number == 2
            assert version.recipe_data == {'name': 'Test Recipe'}
            assert version.change_summary == 'Updated ingredients'
    
    def test_version_to_dict(self, app):
        """Test version to_dict method."""
        with app.app_context():
            version = RecipeVersion(
                recipe_id=uuid.uuid4(),
                version_number=1,
                recipe_data={'test': 'data'},
                change_summary='Initial version'
            )
            
            result = version.to_dict()
            
            assert result['version_number'] == 1
            assert result['recipe_data'] == {'test': 'data'}
            assert result['change_summary'] == 'Initial version'
            assert 'id' in result
            assert 'recipe_id' in result