"""Integration tests for Recipe API endpoints."""
import pytest
import json
import uuid

from app.models.recipe import Recipe, RecipeIngredient, RecipeStatus, IngredientUnit
from app.extensions import db


class TestRecipeAPI:
    """Test cases for Recipe API endpoints."""
    
    def test_create_recipe_success(self, client, app, mock_product_client):
        """Test creating a recipe successfully."""
        with app.app_context():
            db.create_all()
            
            recipe_data = {
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
                        'sort_order': 0
                    },
                    {
                        'ingredient_product_id': str(uuid.uuid4()),
                        'quantity': 2,
                        'unit': 'piece',
                        'sort_order': 1,
                        'is_optional': True
                    }
                ]
            }
            
            response = client.post(
                '/api/v1/recipes/',
                data=json.dumps(recipe_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['name'] == 'Test Recipe'
            assert data['status'] == 'draft'
            assert len(data['ingredients']) == 2
            assert 'id' in data
    
    def test_create_recipe_validation_error(self, client, app, mock_product_client):
        """Test creating recipe with validation errors."""
        with app.app_context():
            db.create_all()
            
            # Missing required fields
            recipe_data = {
                'name': 'Test Recipe'
                # Missing product_id and ingredients
            }
            
            response = client.post(
                '/api/v1/recipes/',
                data=json.dumps(recipe_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
    
    def test_create_recipe_empty_ingredients(self, client, app, mock_product_client):
        """Test creating recipe with empty ingredients list."""
        with app.app_context():
            db.create_all()
            
            recipe_data = {
                'product_id': str(uuid.uuid4()),
                'name': 'Test Recipe',
                'ingredients': []  # Empty ingredients
            }
            
            response = client.post(
                '/api/v1/recipes/',
                data=json.dumps(recipe_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
    
    def test_get_recipe_success(self, client, app, mock_product_client):
        """Test getting recipe by ID successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe directly in database
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                description="Test description",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM,
                sort_order=0
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(f'/api/v1/recipes/{recipe.id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Test Recipe'
            assert data['status'] == 'active'
            assert len(data['ingredients']) == 1
    
    def test_get_recipe_not_found(self, client, app):
        """Test getting nonexistent recipe returns 404."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            response = client.get(f'/api/v1/recipes/{fake_id}')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'not found' in data['message']
    
    def test_get_recipe_by_product_success(self, client, app, mock_product_client):
        """Test getting recipe by product ID successfully."""
        with app.app_context():
            db.create_all()
            
            product_id = uuid.uuid4()
            
            # Create active recipe for product
            recipe = Recipe(
                product_id=product_id,
                name="Product Recipe",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(f'/api/v1/recipes/by-product/{product_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Product Recipe'
            assert data['product_id'] == str(product_id)
    
    def test_get_recipe_by_product_not_found(self, client, app):
        """Test getting recipe by nonexistent product returns 404."""
        with app.app_context():
            db.create_all()
            
            fake_product_id = uuid.uuid4()
            response = client.get(f'/api/v1/recipes/by-product/{fake_product_id}')
            
            assert response.status_code == 404
    
    def test_update_recipe_success(self, client, app, mock_product_client):
        """Test updating recipe successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Original Recipe",
                status=RecipeStatus.DRAFT
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            # Update recipe
            update_data = {
                'name': 'Updated Recipe',
                'status': 'active',
                'description': 'Updated description'
            }
            
            response = client.put(
                f'/api/v1/recipes/{recipe.id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'Updated Recipe'
            assert data['status'] == 'active'
            assert data['description'] == 'Updated description'
    
    def test_update_recipe_not_found(self, client, app):
        """Test updating nonexistent recipe returns 404."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            update_data = {'name': 'Updated Name'}
            
            response = client.put(
                f'/api/v1/recipes/{fake_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 404
    
    def test_delete_recipe_success(self, client, app, mock_product_client):
        """Test deleting recipe successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="To Delete",
                status=RecipeStatus.DRAFT
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            recipe_id = recipe.id
            
            response = client.delete(f'/api/v1/recipes/{recipe_id}')
            
            assert response.status_code == 204
            
            # Verify recipe is deleted
            get_response = client.get(f'/api/v1/recipes/{recipe_id}')
            assert get_response.status_code == 404
    
    def test_delete_recipe_not_found(self, client, app):
        """Test deleting nonexistent recipe returns 404."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            response = client.delete(f'/api/v1/recipes/{fake_id}')
            
            assert response.status_code == 404
    
    def test_get_recipes_list_empty(self, client, app):
        """Test getting recipes when none exist."""
        with app.app_context():
            db.create_all()
            
            response = client.get('/api/v1/recipes/')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['recipes'] == []
            assert data['pagination']['total'] == 0
    
    def test_get_recipes_list_with_pagination(self, client, app, mock_product_client):
        """Test getting recipes with pagination."""
        with app.app_context():
            db.create_all()
            
            # Create test recipes
            for i in range(5):
                recipe = Recipe(
                    product_id=uuid.uuid4(),
                    name=f"Recipe {i}",
                    status=RecipeStatus.ACTIVE
                )
                ingredient = RecipeIngredient(
                    ingredient_product_id=uuid.uuid4(),
                    quantity=100.0,
                    unit=IngredientUnit.GRAM
                )
                recipe.ingredients.append(ingredient)
                db.session.add(recipe)
            
            db.session.commit()
            
            # Test pagination
            response = client.get('/api/v1/recipes/?page=1&per_page=3')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['recipes']) == 3
            assert data['pagination']['total'] == 5
            assert data['pagination']['pages'] == 2
    
    def test_validate_recipe(self, client, app, mock_product_client):
        """Test recipe validation endpoint."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Valid Recipe",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(f'/api/v1/recipes/{recipe.id}/validate')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'is_valid' in data
            assert 'validation_errors' in data
            assert 'recipe_id' in data
    
    def test_get_recipe_hierarchy_success(self, client, app, mock_product_client):
        """Test getting recipe hierarchy successfully."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Hierarchy Test Recipe",
                status=RecipeStatus.ACTIVE,
                yield_quantity=500.0,
                yield_unit=IngredientUnit.GRAM
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(f'/api/v1/recipes/{recipe.id}/hierarchy')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'recipe_id' in data
            assert 'hierarchy' in data
            assert 'max_depth' in data
            assert 'total_items' in data
    
    def test_get_recipe_hierarchy_with_scaling(self, client, app, mock_product_client):
        """Test getting recipe hierarchy with quantity scaling."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe with yield
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Scalable Recipe",
                status=RecipeStatus.ACTIVE,
                yield_quantity=500.0,
                yield_unit=IngredientUnit.GRAM
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(
                f'/api/v1/recipes/{recipe.id}/hierarchy'
                '?target_quantity=1000&target_unit=gram'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['scaling_applied'] is True
            assert data['parameters']['target_quantity'] == 1000.0
    
    def test_get_recipe_hierarchy_invalid_depth(self, client, app):
        """Test hierarchy with invalid depth parameter."""
        with app.app_context():
            db.create_all()
            
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.ACTIVE
            )
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(f'/api/v1/recipes/{recipe.id}/hierarchy?max_depth=25')
            
            assert response.status_code == 400
    
    def test_recipe_analysis_success(self, client, app, mock_product_client):
        """Test recipe analysis endpoint."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe with ingredients
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Analysis Test Recipe",
                status=RecipeStatus.ACTIVE
            )
            
            # Add multiple ingredients
            for i in range(3):
                ingredient = RecipeIngredient(
                    ingredient_product_id=uuid.uuid4(),
                    quantity=100.0 + i * 50,
                    unit=IngredientUnit.GRAM,
                    ingredient_group=f"Group {i % 2}",
                    is_optional=(i == 2)
                )
                recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(f'/api/v1/recipes/{recipe.id}/analysis')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'complexity_metrics' in data
            assert 'dependencies' in data
            assert 'hierarchy_analysis' in data
            assert 'performance_insights' in data
            
            # Check complexity metrics
            complexity = data['complexity_metrics']
            assert complexity['ingredient_count'] == 3
            assert complexity['optional_ingredients'] == 1
            assert complexity['required_ingredients'] == 2
            assert 'complexity_level' in complexity
    
    def test_recipe_analysis_not_found(self, client, app):
        """Test recipe analysis for non-existent recipe."""
        with app.app_context():
            db.create_all()
            
            fake_id = uuid.uuid4()
            response = client.get(f'/api/v1/recipes/{fake_id}/analysis')
            
            assert response.status_code == 404
    
    def test_recipes_by_product_success(self, client, app, mock_product_client):
        """Test getting recipes that use a specific product."""
        with app.app_context():
            db.create_all()
            
            product_id = uuid.uuid4()
            
            # Create recipe using the product
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Recipe Using Product",
                status=RecipeStatus.ACTIVE
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=product_id,
                quantity=200.0,
                unit=IngredientUnit.GRAM,
                ingredient_group="Main",
                is_optional=False,
                notes="Important ingredient"
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            response = client.get(f'/api/v1/recipes/product/{product_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['product_id'] == str(product_id)
            assert data['total_count'] == 1
            assert len(data['recipes']) == 1
            
            # Check usage details
            recipe_data = data['recipes'][0]
            assert 'usage_details' in recipe_data
            usage = recipe_data['usage_details']
            assert usage['quantity'] == 200.0
            assert usage['unit'] == 'gram'
            assert usage['ingredient_group'] == 'Main'
            assert usage['is_optional'] is False
            assert usage['notes'] == 'Important ingredient'
    
    def test_recipes_by_product_empty(self, client, app):
        """Test getting recipes for product not used anywhere."""
        with app.app_context():
            db.create_all()
            
            unused_product_id = uuid.uuid4()
            response = client.get(f'/api/v1/recipes/product/{unused_product_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['product_id'] == str(unused_product_id)
            assert data['total_count'] == 0
            assert data['recipes'] == []
    
    def test_recipe_tags_list(self, client, app):
        """Test getting all recipe tags."""
        with app.app_context():
            db.create_all()
            
            # Create test tags
            tag1 = RecipeTag(name="dessert", color="#FF69B4")
            tag2 = RecipeTag(name="quick", color="#90EE90")
            
            db.session.add_all([tag1, tag2])
            db.session.commit()
            
            response = client.get('/api/v1/recipes/tags')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 2
            
            # Should be sorted by name
            assert data[0]['name'] == 'dessert'
            assert data[1]['name'] == 'quick'
    
    def test_update_recipe_ingredient_success(self, client, app, mock_product_client):
        """Test updating a recipe ingredient."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe with ingredient
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM,
                notes="Original notes"
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            
            # Update ingredient
            update_data = {
                'quantity': 150.0,
                'notes': 'Updated notes',
                'is_optional': True
            }
            
            response = client.put(
                f'/api/v1/recipes/{recipe.id}/ingredients/{ingredient.id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert float(data['quantity']) == 150.0
            assert data['notes'] == 'Updated notes'
            assert data['is_optional'] is True
    
    def test_delete_recipe_ingredient_success(self, client, app, mock_product_client):
        """Test deleting a recipe ingredient."""
        with app.app_context():
            db.create_all()
            
            # Create test recipe with ingredient
            recipe = Recipe(
                product_id=uuid.uuid4(),
                name="Test Recipe",
                status=RecipeStatus.DRAFT
            )
            
            ingredient = RecipeIngredient(
                ingredient_product_id=uuid.uuid4(),
                quantity=100.0,
                unit=IngredientUnit.GRAM
            )
            recipe.ingredients.append(ingredient)
            
            db.session.add(recipe)
            db.session.commit()
            ingredient_id = ingredient.id
            
            response = client.delete(f'/api/v1/recipes/{recipe.id}/ingredients/{ingredient_id}')
            
            assert response.status_code == 204
            
            # Verify deletion
            response = client.get(f'/api/v1/recipes/{recipe.id}')
            data = json.loads(response.data)
            assert len(data['ingredients']) == 0
    
    def test_recipe_validation_edge_cases(self, client, app, mock_product_client):
        """Test recipe validation with edge cases."""
        with app.app_context():
            db.create_all()
            
            # Test recipe with very long name
            long_name = "A" * 300  # Exceeds 255 char limit
            recipe_data = {
                'product_id': str(uuid.uuid4()),
                'name': long_name,
                'ingredients': [
                    {
                        'ingredient_product_id': str(uuid.uuid4()),
                        'quantity': 100.0,
                        'unit': 'gram'
                    }
                ]
            }
            
            response = client.post(
                '/api/v1/recipes/',
                data=json.dumps(recipe_data),
                content_type='application/json'
            )
            
            # Should fail validation
            assert response.status_code == 400
    
    def test_recipe_ingredient_duplicate_prevention(self, client, app, mock_product_client):
        """Test prevention of duplicate ingredients in recipe."""
        with app.app_context():
            db.create_all()
            
            ingredient_id = str(uuid.uuid4())
            recipe_data = {
                'product_id': str(uuid.uuid4()),
                'name': 'Duplicate Test Recipe',
                'ingredients': [
                    {
                        'ingredient_product_id': ingredient_id,
                        'quantity': 100.0,
                        'unit': 'gram'
                    },
                    {
                        'ingredient_product_id': ingredient_id,  # Duplicate!
                        'quantity': 50.0,
                        'unit': 'piece'
                    }
                ]
            }
            
            response = client.post(
                '/api/v1/recipes/',
                data=json.dumps(recipe_data),
                content_type='application/json'
            )
            
            # Should fail validation due to duplicates
            assert response.status_code == 400
    
    def test_recipe_pagination_edge_cases(self, client, app):
        """Test recipe pagination with edge cases."""
        with app.app_context():
            db.create_all()
            
            # Test with page beyond available pages
            response = client.get('/api/v1/recipes/?page=999&per_page=10')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['recipes'] == []
            assert data['pagination']['total'] == 0
    
    def test_recipe_status_transitions(self, client, app, mock_product_client):
        """Test recipe status transitions."""
        with app.app_context():
            db.create_all()
            
            # Create draft recipe
            recipe_data = {
                'product_id': str(uuid.uuid4()),
                'name': 'Status Test Recipe',
                'status': 'draft',
                'ingredients': [
                    {
                        'ingredient_product_id': str(uuid.uuid4()),
                        'quantity': 100.0,
                        'unit': 'gram'
                    }
                ]
            }
            
            response = client.post(
                '/api/v1/recipes/',
                data=json.dumps(recipe_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            recipe_id = json.loads(response.data)['id']
            
            # Transition to active
            update_data = {'status': 'active'}
            response = client.put(
                f'/api/v1/recipes/{recipe_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'active'
            
            # Transition to archived
            update_data = {'status': 'archived'}
            response = client.put(
                f'/api/v1/recipes/{recipe_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'archived'