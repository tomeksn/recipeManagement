"""Unit tests for Recipe models."""
import pytest
import uuid
from decimal import Decimal
from datetime import datetime

from app.models.recipe import (
    Recipe, RecipeIngredient, RecipeVersion, RecipeDependency,
    RecipeNutrition, RecipeTag, RecipeAudit, RecipeStatus, IngredientUnit
)
from app.extensions import db
from app.utils.exceptions import RecipeValidationError


class TestRecipeModel:
    """Test cases for Recipe model."""
    
    def test_recipe_creation(self, app):
        """Test creating a recipe with valid data."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                description="A test recipe",
                status=RecipeStatus.DRAFT,
                yield_quantity=Decimal('500.0'),
                yield_unit=IngredientUnit.GRAM,
                preparation_time=30
            )
            
            db.session.add(recipe)
            db.session.commit()
            
            assert recipe.id is not None
            assert recipe.name == "Test Recipe"
            assert recipe.status == RecipeStatus.DRAFT
            assert recipe.version == 1
            assert recipe.yield_quantity == Decimal('500.0')
            assert recipe.yield_unit == IngredientUnit.GRAM
            assert recipe.preparation_time == 30
    
    def test_recipe_validation_empty_name(self, app):
        """Test recipe validation with empty name."""
        with app.app_context():
            db.create_all()
            
            with pytest.raises(Exception):  # Should trigger database constraint
                recipe = Recipe(
                    product_id=uuid.uuid4(),
                    name="",  # Empty name should fail
                    status=RecipeStatus.DRAFT
                )
                db.session.add(recipe)
                db.session.commit()
    
    def test_recipe_validation_negative_yield(self, app):
        """Test recipe validation with negative yield quantity."""
        with app.app_context():
            db.create_all()
            
            with pytest.raises(Exception):  # Should trigger database constraint
                recipe = Recipe(
                    product_id=uuid.uuid4(),
                    name="Test Recipe",
                    status=RecipeStatus.DRAFT,
                    yield_quantity=Decimal('-100.0')  # Negative yield should fail
                )
                db.session.add(recipe)
                db.session.commit()
    
    def test_recipe_to_dict(self, app):
        """Test recipe serialization to dictionary."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                description="A test recipe",
                status=RecipeStatus.ACTIVE
            )
            
            db.session.add(recipe)
            db.session.commit()
            
            recipe_dict = recipe.to_dict()
            
            assert recipe_dict['id'] == str(recipe.id)
            assert recipe_dict['name'] == "Test Recipe"
            assert recipe_dict['description'] == "A test recipe"
            assert recipe_dict['status'] == "active"
            assert recipe_dict['version'] == 1
    
    def test_recipe_version_increment(self, app):
        """Test recipe version incrementation."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            
            db.session.add(recipe)
            db.session.commit()
            
            initial_version = recipe.version
            recipe.increment_version()
            
            assert recipe.version == initial_version + 1


class TestRecipeIngredientModel:
    """Test cases for RecipeIngredient model."""
    
    def test_ingredient_creation(self, app):
        """Test creating a recipe ingredient."""
        with app.app_context():
            db.create_all()
            
            # Create parent recipe first
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
                quantity=Decimal('100.5'),
                unit=IngredientUnit.GRAM,
                sort_order=1,
                ingredient_group="Base",
                is_optional=False
            )
            
            db.session.add(ingredient)
            db.session.commit()
            
            assert ingredient.id is not None
            assert ingredient.recipe_id == recipe.id
            assert ingredient.quantity == Decimal('100.5')
            assert ingredient.unit == IngredientUnit.GRAM
            assert ingredient.sort_order == 1
            assert ingredient.ingredient_group == "Base"
            assert ingredient.is_optional is False
    
    def test_ingredient_validation_negative_quantity(self, app):
        """Test ingredient validation with negative quantity."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            with pytest.raises(Exception):  # Should trigger database constraint
                ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_product_id=uuid.uuid4(),
                    quantity=Decimal('-50.0'),  # Negative quantity should fail
                    unit=IngredientUnit.GRAM
                )
                db.session.add(ingredient)
                db.session.commit()
    
    def test_ingredient_to_dict(self, app):
        """Test ingredient serialization to dictionary."""
        with app.app_context():
            db.create_all()
            
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
                quantity=Decimal('250.0'),
                unit=IngredientUnit.GRAM,
                sort_order=2,
                ingredient_group="Main",
                notes="Test notes",
                is_optional=True
            )
            
            db.session.add(ingredient)
            db.session.commit()
            
            ingredient_dict = ingredient.to_dict()
            
            assert ingredient_dict['id'] == str(ingredient.id)
            assert ingredient_dict['recipe_id'] == str(recipe.id)
            assert float(ingredient_dict['quantity']) == 250.0
            assert ingredient_dict['unit'] == "gram"
            assert ingredient_dict['sort_order'] == 2
            assert ingredient_dict['ingredient_group'] == "Main"
            assert ingredient_dict['notes'] == "Test notes"
            assert ingredient_dict['is_optional'] is True


class TestRecipeVersionModel:
    """Test cases for RecipeVersion model."""
    
    def test_version_creation(self, app):
        """Test creating a recipe version."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            version_data = {
                'name': 'Test Recipe',
                'ingredients': [],
                'version': 1
            }
            
            version = RecipeVersion(
                recipe_id=recipe.id,
                version_number=1,
                recipe_data=version_data,
                change_summary="Initial version",
                created_by=uuid.uuid4()
            )
            
            db.session.add(version)
            db.session.commit()
            
            assert version.id is not None
            assert version.recipe_id == recipe.id
            assert version.version_number == 1
            assert version.recipe_data == version_data
            assert version.change_summary == "Initial version"


class TestRecipeDependencyModel:
    """Test cases for RecipeDependency model."""
    
    def test_dependency_creation(self, app):
        """Test creating a recipe dependency."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            dependency = RecipeDependency(
                parent_recipe_id=recipe.id,
                child_product_id=uuid.uuid4(),
                dependency_type="ingredient",
                depth_level=1
            )
            
            db.session.add(dependency)
            db.session.commit()
            
            assert dependency.id is not None
            assert dependency.parent_recipe_id == recipe.id
            assert dependency.dependency_type == "ingredient"
            assert dependency.depth_level == 1


class TestRecipeNutritionModel:
    """Test cases for RecipeNutrition model."""
    
    def test_nutrition_creation(self, app):
        """Test creating recipe nutrition information."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            nutrition = RecipeNutrition(
                recipe_id=recipe.id,
                calories=Decimal('250.5'),
                protein=Decimal('15.2'),
                carbohydrates=Decimal('30.0'),
                fat=Decimal('12.5'),
                fiber=Decimal('5.0'),
                calculation_method="automated"
            )
            
            db.session.add(nutrition)
            db.session.commit()
            
            assert nutrition.recipe_id == recipe.id
            assert nutrition.calories == Decimal('250.5')
            assert nutrition.protein == Decimal('15.2')
            assert nutrition.calculation_method == "automated"
    
    def test_nutrition_validation_negative_values(self, app):
        """Test nutrition validation with negative values."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            with pytest.raises(Exception):  # Should trigger database constraint
                nutrition = RecipeNutrition(
                    recipe_id=recipe.id,
                    calories=Decimal('-100.0'),  # Negative calories should fail
                    protein=Decimal('15.0')
                )
                db.session.add(nutrition)
                db.session.commit()


class TestRecipeTagModel:
    """Test cases for RecipeTag model."""
    
    def test_tag_creation(self, app):
        """Test creating a recipe tag."""
        with app.app_context():
            db.create_all()
            
            tag = RecipeTag(
                name="dessert",
                color="#FF69B4",
                description="Sweet dessert recipes"
            )
            
            db.session.add(tag)
            db.session.commit()
            
            assert tag.id is not None
            assert tag.name == "dessert"
            assert tag.color == "#FF69B4"
            assert tag.description == "Sweet dessert recipes"
    
    def test_tag_validation_invalid_color(self, app):
        """Test tag validation with invalid color format."""
        with app.app_context():
            db.create_all()
            
            with pytest.raises(Exception):  # Should trigger database constraint
                tag = RecipeTag(
                    name="test",
                    color="invalid_color"  # Invalid hex color
                )
                db.session.add(tag)
                db.session.commit()
    
    def test_tag_unique_name_constraint(self, app):
        """Test tag unique name constraint."""
        with app.app_context():
            db.create_all()
            
            # Create first tag
            tag1 = RecipeTag(name="unique_tag")
            db.session.add(tag1)
            db.session.commit()
            
            # Try to create second tag with same name
            with pytest.raises(Exception):  # Should trigger unique constraint
                tag2 = RecipeTag(name="unique_tag")
                db.session.add(tag2)
                db.session.commit()


class TestRecipeAuditModel:
    """Test cases for RecipeAudit model."""
    
    def test_audit_creation(self, app):
        """Test creating a recipe audit entry."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            audit = RecipeAudit(
                recipe_id=recipe.id,
                operation="INSERT",
                table_name="recipes",
                old_values=None,
                new_values={"name": "Test Recipe"},
                changed_by=uuid.uuid4()
            )
            
            db.session.add(audit)
            db.session.commit()
            
            assert audit.audit_id is not None
            assert audit.recipe_id == recipe.id
            assert audit.operation == "INSERT"
            assert audit.table_name == "recipes"
            assert audit.new_values == {"name": "Test Recipe"}


class TestRecipeRelationships:
    """Test cases for Recipe model relationships."""
    
    def test_recipe_ingredients_relationship(self, app):
        """Test recipe-ingredients relationship."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            # Add ingredients
            ingredient1 = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM,
                sort_order=1
            )
            
            ingredient2 = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=uuid.uuid4(),
                quantity=Decimal('2'),
                unit=IngredientUnit.PIECE,
                sort_order=2
            )
            
            db.session.add_all([ingredient1, ingredient2])
            db.session.commit()
            
            # Test relationship
            assert len(recipe.ingredients) == 2
            assert recipe.ingredients[0].sort_order == 1
            assert recipe.ingredients[1].sort_order == 2
    
    def test_recipe_tags_relationship(self, app):
        """Test recipe-tags many-to-many relationship."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            
            tag1 = RecipeTag(name="dessert")
            tag2 = RecipeTag(name="quick")
            
            db.session.add_all([recipe, tag1, tag2])
            db.session.flush()
            
            # Associate tags with recipe
            recipe.tags = [tag1, tag2]
            db.session.commit()
            
            # Test relationship
            assert len(recipe.tags) == 2
            assert tag1 in recipe.tags
            assert tag2 in recipe.tags
    
    def test_recipe_nutrition_relationship(self, app):
        """Test recipe-nutrition one-to-one relationship."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            nutrition = RecipeNutrition(
                recipe_id=recipe.id,
                calories=Decimal('300.0'),
                protein=Decimal('20.0')
            )
            db.session.add(nutrition)
            db.session.commit()
            
            # Test relationship
            assert recipe.nutrition is not None
            assert recipe.nutrition.calories == Decimal('300.0')
            assert recipe.nutrition.protein == Decimal('20.0')


class TestRecipeBusinessLogic:
    """Test cases for Recipe business logic methods."""
    
    def test_get_total_ingredients_count(self, app):
        """Test getting total ingredients count."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            # Add ingredients
            for i in range(3):
                ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_product_id=uuid.uuid4(),
                    quantity=Decimal('100.0'),
                    unit=IngredientUnit.GRAM
                )
                db.session.add(ingredient)
            
            db.session.commit()
            
            assert recipe.get_total_ingredients_count() == 3
    
    def test_has_ingredient(self, app):
        """Test checking if recipe has specific ingredient."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            db.session.add(recipe)
            db.session.flush()
            
            product_id = uuid.uuid4()
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=product_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            db.session.add(ingredient)
            db.session.commit()
            
            assert recipe.has_ingredient(product_id) is True
            assert recipe.has_ingredient(uuid.uuid4()) is False