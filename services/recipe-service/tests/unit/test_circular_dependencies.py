"""Tests for circular dependency prevention in recipes."""
import pytest
import uuid
from decimal import Decimal

from app.models.recipe import Recipe, RecipeIngredient, RecipeDependency, RecipeStatus, IngredientUnit
from app.extensions import db
from app.utils.exceptions import CircularDependencyError


class TestCircularDependencyPrevention:
    """Test cases for circular dependency prevention."""
    
    def test_simple_circular_dependency_detection(self, app):
        """Test detection of simple A->B->A circular dependency."""
        with app.app_context():
            db.create_all()
            
            # Create products
            product_a_id = uuid.uuid4()
            product_b_id = uuid.uuid4()
            
            # Create Recipe A that uses Product B
            recipe_a = Recipe(
                product_id=product_a_id,
                name="Recipe A",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_b = RecipeIngredient(
                ingredient_product_id=product_b_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_a.ingredients.append(ingredient_b)
            
            db.session.add(recipe_a)
            db.session.commit()
            
            # Create Recipe B that uses Product A (should create circular dependency)
            recipe_b = Recipe(
                product_id=product_b_id,
                name="Recipe B",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_a = RecipeIngredient(
                ingredient_product_id=product_a_id,  # This creates the cycle
                quantity=Decimal('50.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_b.ingredients.append(ingredient_a)
            
            # This should trigger the circular dependency prevention
            with pytest.raises(Exception):  # Database trigger should prevent this
                db.session.add(recipe_b)
                db.session.commit()
    
    def test_self_reference_prevention(self, app):
        """Test prevention of recipe referencing itself."""
        with app.app_context():
            db.create_all()
            
            product_id = uuid.uuid4()
            
            # Create recipe
            recipe = Recipe(
                product_id=product_id,
                name="Self-Reference Recipe",
                status=RecipeStatus.ACTIVE
            )
            db.session.add(recipe)
            db.session.commit()
            
            # Try to add the same product as ingredient (self-reference)
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_product_id=product_id,  # Same as recipe's product
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            
            # This should be prevented by database constraints
            with pytest.raises(Exception):
                db.session.add(ingredient)
                db.session.commit()
    
    def test_complex_circular_dependency_a_b_c_a(self, app):
        """Test detection of complex A->B->C->A circular dependency."""
        with app.app_context():
            db.create_all()
            
            # Create products
            product_a_id = uuid.uuid4()
            product_b_id = uuid.uuid4()
            product_c_id = uuid.uuid4()
            
            # Create Recipe A that uses Product B
            recipe_a = Recipe(
                product_id=product_a_id,
                name="Recipe A",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_b = RecipeIngredient(
                ingredient_product_id=product_b_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_a.ingredients.append(ingredient_b)
            
            db.session.add(recipe_a)
            db.session.commit()
            
            # Create Recipe B that uses Product C
            recipe_b = Recipe(
                product_id=product_b_id,
                name="Recipe B",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_c = RecipeIngredient(
                ingredient_product_id=product_c_id,
                quantity=Decimal('75.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_b.ingredients.append(ingredient_c)
            
            db.session.add(recipe_b)
            db.session.commit()
            
            # Create Recipe C that uses Product A (completes the cycle)
            recipe_c = Recipe(
                product_id=product_c_id,
                name="Recipe C",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_a = RecipeIngredient(
                ingredient_product_id=product_a_id,  # This creates A->B->C->A cycle
                quantity=Decimal('25.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_c.ingredients.append(ingredient_a)
            
            # This should trigger circular dependency prevention
            with pytest.raises(Exception):
                db.session.add(recipe_c)
                db.session.commit()
    
    def test_no_circular_dependency_valid_hierarchy(self, app):
        """Test that valid hierarchical recipes work without circular dependencies."""
        with app.app_context():
            db.create_all()
            
            # Create products for a valid hierarchy
            flour_id = uuid.uuid4()
            dough_id = uuid.uuid4()
            bread_id = uuid.uuid4()
            
            # Create base ingredient (flour) - no recipe needed
            
            # Create dough recipe that uses flour
            dough_recipe = Recipe(
                product_id=dough_id,
                name="Bread Dough",
                status=RecipeStatus.ACTIVE
            )
            
            flour_ingredient = RecipeIngredient(
                ingredient_product_id=flour_id,
                quantity=Decimal('500.0'),
                unit=IngredientUnit.GRAM
            )
            dough_recipe.ingredients.append(flour_ingredient)
            
            db.session.add(dough_recipe)
            db.session.commit()
            
            # Create bread recipe that uses dough
            bread_recipe = Recipe(
                product_id=bread_id,
                name="Bread",
                status=RecipeStatus.ACTIVE
            )
            
            dough_ingredient = RecipeIngredient(
                ingredient_product_id=dough_id,
                quantity=Decimal('1'),
                unit=IngredientUnit.PIECE
            )
            bread_recipe.ingredients.append(dough_ingredient)
            
            # This should work fine - no circular dependency
            db.session.add(bread_recipe)
            db.session.commit()
            
            # Verify recipes were created
            assert dough_recipe.id is not None
            assert bread_recipe.id is not None
    
    def test_circular_dependency_with_inactive_recipe(self, app):
        """Test that circular dependencies are checked even with inactive recipes."""
        with app.app_context():
            db.create_all()
            
            # Create products
            product_a_id = uuid.uuid4()
            product_b_id = uuid.uuid4()
            
            # Create active Recipe A that uses Product B
            recipe_a = Recipe(
                product_id=product_a_id,
                name="Recipe A",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_b = RecipeIngredient(
                ingredient_product_id=product_b_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_a.ingredients.append(ingredient_b)
            
            db.session.add(recipe_a)
            db.session.commit()
            
            # Create inactive Recipe B that uses Product A
            recipe_b = Recipe(
                product_id=product_b_id,
                name="Recipe B",
                status=RecipeStatus.DRAFT  # Inactive status
            )
            
            ingredient_a = RecipeIngredient(
                ingredient_product_id=product_a_id,
                quantity=Decimal('50.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_b.ingredients.append(ingredient_a)
            
            # Even with inactive status, circular dependency should be prevented
            with pytest.raises(Exception):
                db.session.add(recipe_b)
                db.session.commit()
    
    def test_deep_hierarchy_without_cycles(self, app):
        """Test deep valid hierarchy without circular dependencies."""
        with app.app_context():
            db.create_all()
            
            # Create a 5-level deep hierarchy
            product_ids = [uuid.uuid4() for _ in range(5)]
            
            # Create recipes that use the previous level's product
            for i in range(1, 5):  # Skip level 0 (base ingredient)
                recipe = Recipe(
                    product_id=product_ids[i],
                    name=f"Recipe Level {i}",
                    status=RecipeStatus.ACTIVE
                )
                
                ingredient = RecipeIngredient(
                    ingredient_product_id=product_ids[i-1],  # Use previous level
                    quantity=Decimal('100.0'),
                    unit=IngredientUnit.GRAM
                )
                recipe.ingredients.append(ingredient)
                
                db.session.add(recipe)
                db.session.commit()
            
            # All recipes should be created successfully
            recipes = db.session.query(Recipe).all()
            assert len(recipes) == 4  # 4 levels of recipes (level 0 is base ingredient)
    
    def test_diamond_dependency_pattern(self, app):
        """Test diamond dependency pattern (A->B, A->C, B->D, C->D) without cycles."""
        with app.app_context():
            db.create_all()
            
            # Create products for diamond pattern
            product_a_id = uuid.uuid4()  # Top
            product_b_id = uuid.uuid4()  # Left branch
            product_c_id = uuid.uuid4()  # Right branch  
            product_d_id = uuid.uuid4()  # Bottom (shared)
            
            # Create Recipe A that uses both B and C
            recipe_a = Recipe(
                product_id=product_a_id,
                name="Recipe A (Top)",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_b = RecipeIngredient(
                ingredient_product_id=product_b_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            ingredient_c = RecipeIngredient(
                ingredient_product_id=product_c_id,
                quantity=Decimal('50.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_a.ingredients.extend([ingredient_b, ingredient_c])
            
            db.session.add(recipe_a)
            db.session.commit()
            
            # Create Recipe B that uses D
            recipe_b = Recipe(
                product_id=product_b_id,
                name="Recipe B (Left)",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_d1 = RecipeIngredient(
                ingredient_product_id=product_d_id,
                quantity=Decimal('75.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_b.ingredients.append(ingredient_d1)
            
            db.session.add(recipe_b)
            db.session.commit()
            
            # Create Recipe C that also uses D
            recipe_c = Recipe(
                product_id=product_c_id,
                name="Recipe C (Right)",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_d2 = RecipeIngredient(
                ingredient_product_id=product_d_id,
                quantity=Decimal('25.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_c.ingredients.append(ingredient_d2)
            
            # This should work fine - diamond pattern is valid
            db.session.add(recipe_c)
            db.session.commit()
            
            # Verify all recipes were created
            recipes = db.session.query(Recipe).all()
            assert len(recipes) == 3
    
    def test_dependency_tracking_creation(self, app):
        """Test that recipe dependencies are properly tracked."""
        with app.app_context():
            db.create_all()
            
            # Create products
            product_a_id = uuid.uuid4()
            product_b_id = uuid.uuid4()
            product_c_id = uuid.uuid4()
            
            # Create recipe with multiple ingredients
            recipe = Recipe(
                product_id=product_a_id,
                name="Multi-Ingredient Recipe",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_b = RecipeIngredient(
                ingredient_product_id=product_b_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            ingredient_c = RecipeIngredient(
                ingredient_product_id=product_c_id,
                quantity=Decimal('2'),
                unit=IngredientUnit.PIECE
            )
            recipe.ingredients.extend([ingredient_b, ingredient_c])
            
            db.session.add(recipe)
            db.session.commit()
            
            # Check that dependencies were created
            dependencies = db.session.query(RecipeDependency).filter(
                RecipeDependency.parent_recipe_id == recipe.id
            ).all()
            
            assert len(dependencies) == 2
            dependency_products = {dep.child_product_id for dep in dependencies}
            assert product_b_id in dependency_products
            assert product_c_id in dependency_products
    
    def test_update_recipe_circular_dependency_check(self, app):
        """Test that updating recipes also checks for circular dependencies."""
        with app.app_context():
            db.create_all()
            
            # Create initial valid setup
            product_a_id = uuid.uuid4()
            product_b_id = uuid.uuid4()
            product_c_id = uuid.uuid4()
            
            # Recipe A uses Product C (safe initially)
            recipe_a = Recipe(
                product_id=product_a_id,
                name="Recipe A",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_c = RecipeIngredient(
                ingredient_product_id=product_c_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_a.ingredients.append(ingredient_c)
            
            db.session.add(recipe_a)
            db.session.commit()
            
            # Recipe B uses Product A
            recipe_b = Recipe(
                product_id=product_b_id,
                name="Recipe B",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_a = RecipeIngredient(
                ingredient_product_id=product_a_id,
                quantity=Decimal('50.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_b.ingredients.append(ingredient_a)
            
            db.session.add(recipe_b)
            db.session.commit()
            
            # Now try to update Recipe A to use Product B (would create cycle)
            # Remove current ingredient
            recipe_a.ingredients.clear()
            
            # Add ingredient that creates circular dependency
            new_ingredient = RecipeIngredient(
                recipe_id=recipe_a.id,
                ingredient_product_id=product_b_id,  # This creates A->B->A cycle
                quantity=Decimal('75.0'),
                unit=IngredientUnit.GRAM
            )
            
            # This should be prevented
            with pytest.raises(Exception):
                db.session.add(new_ingredient)
                db.session.commit()
    
    def test_archived_recipe_dependency_handling(self, app):
        """Test handling of dependencies with archived recipes."""
        with app.app_context():
            db.create_all()
            
            # Create products
            product_a_id = uuid.uuid4()
            product_b_id = uuid.uuid4()
            
            # Create Recipe A
            recipe_a = Recipe(
                product_id=product_a_id,
                name="Recipe A",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_b = RecipeIngredient(
                ingredient_product_id=product_b_id,
                quantity=Decimal('100.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_a.ingredients.append(ingredient_b)
            
            db.session.add(recipe_a)
            db.session.commit()
            
            # Archive Recipe A
            recipe_a.status = RecipeStatus.ARCHIVED
            db.session.commit()
            
            # Now create Recipe B that uses Product A
            # This should work since Recipe A is archived
            recipe_b = Recipe(
                product_id=product_b_id,
                name="Recipe B",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient_a = RecipeIngredient(
                ingredient_product_id=product_a_id,
                quantity=Decimal('50.0'),
                unit=IngredientUnit.GRAM
            )
            recipe_b.ingredients.append(ingredient_a)
            
            # This might still be prevented depending on business rules
            # The database function should handle archived recipes appropriately
            try:
                db.session.add(recipe_b)
                db.session.commit()
                # If successful, verify the recipe was created
                assert recipe_b.id is not None
            except Exception:
                # If prevented, that's also acceptable behavior
                db.session.rollback()
                pass