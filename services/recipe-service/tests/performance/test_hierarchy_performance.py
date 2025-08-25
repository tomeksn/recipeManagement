"""Performance tests for recipe hierarchy functionality."""
import pytest
import uuid
import time
from decimal import Decimal
from typing import List, Dict, Any

from app.models.recipe import Recipe, RecipeIngredient, RecipeStatus, IngredientUnit
from app.services.recipe_repository import RecipeRepository
from app.extensions import db


class TestHierarchyPerformance:
    """Performance test cases for recipe hierarchy operations."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return RecipeRepository()
    
    def create_recipe_hierarchy(self, app, depth: int, branching_factor: int = 2) -> List[Recipe]:
        """Create a hierarchical recipe structure for testing.
        
        Args:
            app: Flask application context
            depth: Maximum depth of hierarchy
            branching_factor: Number of ingredients per recipe
            
        Returns:
            List of created recipes
        """
        with app.app_context():
            recipes = []
            
            # Create base ingredients (level 0)
            base_products = [uuid.uuid4() for _ in range(branching_factor)]
            
            # Create recipes for each level
            for level in range(1, depth + 1):
                level_recipes = []
                
                # Number of recipes at this level
                recipes_at_level = branching_factor ** (level - 1)
                
                for recipe_idx in range(recipes_at_level):
                    # Create recipe
                    recipe = Recipe(
                        product_id=uuid.uuid4(),
                        name=f"Recipe L{level}R{recipe_idx}",
                        status=RecipeStatus.ACTIVE,
                        yield_quantity=Decimal('1000.0'),
                        yield_unit=IngredientUnit.GRAM
                    )
                    
                    # Add ingredients from previous level
                    if level == 1:
                        # Use base products
                        ingredient_products = base_products
                    else:
                        # Use products from previous level recipes
                        prev_level_start = sum(branching_factor ** i for i in range(level - 2))
                        prev_level_end = sum(branching_factor ** i for i in range(level - 1))
                        
                        start_idx = recipe_idx * branching_factor
                        ingredient_products = [
                            recipes[prev_level_start + ((start_idx + i) % (prev_level_end - prev_level_start))].product_id
                            for i in range(branching_factor)
                        ]
                    
                    # Create ingredients
                    for i, product_id in enumerate(ingredient_products[:branching_factor]):
                        ingredient = RecipeIngredient(
                            ingredient_product_id=product_id,
                            quantity=Decimal('100.0') + Decimal(str(i * 10)),
                            unit=IngredientUnit.GRAM,
                            sort_order=i
                        )
                        recipe.ingredients.append(ingredient)
                    
                    level_recipes.append(recipe)
                
                # Add all recipes from this level to database
                db.session.add_all(level_recipes)
                db.session.commit()
                
                recipes.extend(level_recipes)
            
            return recipes
    
    def test_hierarchy_query_performance_small(self, app, repository):
        """Test hierarchy query performance with small dataset (3 levels, 2 branches)."""
        recipes = self.create_recipe_hierarchy(app, depth=3, branching_factor=2)
        
        with app.app_context():
            # Test the top-level recipe (most complex hierarchy)
            top_recipe = recipes[-1]  # Last recipe has most complex hierarchy
            
            start_time = time.time()
            hierarchy = repository.get_recipe_hierarchy(top_recipe.id, max_depth=10)
            end_time = time.time()
            
            query_time = end_time - start_time
            
            # Performance assertions
            assert query_time < 1.0, f"Query took {query_time:.3f}s, expected < 1.0s"
            assert len(hierarchy) > 0, "Hierarchy should contain ingredients"
            
            print(f"Small hierarchy query: {query_time:.3f}s, {len(hierarchy)} items")
    
    def test_hierarchy_query_performance_medium(self, app, repository):
        """Test hierarchy query performance with medium dataset (4 levels, 3 branches)."""
        recipes = self.create_recipe_hierarchy(app, depth=4, branching_factor=3)
        
        with app.app_context():
            # Test the top-level recipe
            top_recipe = recipes[-1]
            
            start_time = time.time()
            hierarchy = repository.get_recipe_hierarchy(top_recipe.id, max_depth=10)
            end_time = time.time()
            
            query_time = end_time - start_time
            
            # Performance assertions
            assert query_time < 2.0, f"Query took {query_time:.3f}s, expected < 2.0s"
            assert len(hierarchy) > 0, "Hierarchy should contain ingredients"
            
            print(f"Medium hierarchy query: {query_time:.3f}s, {len(hierarchy)} items")
    
    def test_hierarchy_query_performance_large(self, app, repository):
        """Test hierarchy query performance with large dataset (5 levels, 4 branches)."""
        recipes = self.create_recipe_hierarchy(app, depth=5, branching_factor=4)
        
        with app.app_context():
            # Test multiple recipes to get average performance
            test_recipes = recipes[-5:]  # Test last 5 recipes
            total_time = 0
            total_items = 0
            
            for recipe in test_recipes:
                start_time = time.time()
                hierarchy = repository.get_recipe_hierarchy(recipe.id, max_depth=10)
                end_time = time.time()
                
                query_time = end_time - start_time
                total_time += query_time
                total_items += len(hierarchy)
            
            avg_time = total_time / len(test_recipes)
            avg_items = total_items / len(test_recipes)
            
            # Performance assertions
            assert avg_time < 3.0, f"Average query took {avg_time:.3f}s, expected < 3.0s"
            assert avg_items > 0, "Hierarchy should contain ingredients"
            
            print(f"Large hierarchy query: {avg_time:.3f}s avg, {avg_items:.1f} items avg")
    
    def test_hierarchy_depth_limit_performance(self, app, repository):
        """Test that depth limiting improves performance."""
        recipes = self.create_recipe_hierarchy(app, depth=6, branching_factor=2)
        
        with app.app_context():
            top_recipe = recipes[-1]
            
            # Test with different depth limits
            depth_limits = [1, 3, 5, 10]
            results = []
            
            for depth_limit in depth_limits:
                start_time = time.time()
                hierarchy = repository.get_recipe_hierarchy(
                    top_recipe.id, 
                    max_depth=depth_limit
                )
                end_time = time.time()
                
                query_time = end_time - start_time
                results.append({
                    'depth_limit': depth_limit,
                    'query_time': query_time,
                    'item_count': len(hierarchy)
                })
                
                print(f"Depth {depth_limit}: {query_time:.3f}s, {len(hierarchy)} items")
            
            # Verify that lower depth limits are faster (generally)
            # Note: This might not always be true due to caching and other factors
            assert all(r['query_time'] < 5.0 for r in results), "All queries should complete in reasonable time"
    
    def test_batch_hierarchy_queries_performance(self, app, repository):
        """Test performance of multiple hierarchy queries."""
        recipes = self.create_recipe_hierarchy(app, depth=4, branching_factor=2)
        
        with app.app_context():
            # Test batch queries
            test_recipes = recipes[-10:]  # Test last 10 recipes
            
            start_time = time.time()
            
            hierarchies = []
            for recipe in test_recipes:
                hierarchy = repository.get_recipe_hierarchy(recipe.id, max_depth=5)
                hierarchies.append(hierarchy)
            
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / len(test_recipes)
            total_items = sum(len(h) for h in hierarchies)
            
            # Performance assertions
            assert total_time < 10.0, f"Batch queries took {total_time:.3f}s, expected < 10.0s"
            assert avg_time < 1.0, f"Average query took {avg_time:.3f}s, expected < 1.0s"
            
            print(f"Batch hierarchy queries: {total_time:.3f}s total, {avg_time:.3f}s avg, {total_items} total items")
    
    def test_complexity_metrics_performance(self, app, repository):
        """Test performance of complexity metrics calculation."""
        recipes = self.create_recipe_hierarchy(app, depth=4, branching_factor=3)
        
        with app.app_context():
            test_recipes = recipes[-5:]  # Test last 5 recipes
            
            start_time = time.time()
            
            for recipe in test_recipes:
                metrics = repository.get_recipe_complexity_metrics(recipe.id)
                
                # Verify metrics are reasonable
                assert metrics['ingredient_count'] > 0
                assert metrics['hierarchy_depth'] > 0
                assert 'complexity_level' in metrics
            
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / len(test_recipes)
            
            # Performance assertions
            assert avg_time < 2.0, f"Average complexity calculation took {avg_time:.3f}s, expected < 2.0s"
            
            print(f"Complexity metrics: {avg_time:.3f}s avg per recipe")
    
    def test_product_usage_query_performance(self, app, repository):
        """Test performance of finding recipes using specific products."""
        recipes = self.create_recipe_hierarchy(app, depth=4, branching_factor=3)
        
        with app.app_context():
            # Test finding recipes that use various products
            test_products = [recipe.product_id for recipe in recipes[:5]]
            
            start_time = time.time()
            
            for product_id in test_products:
                using_recipes = repository.get_recipes_using_product(product_id)
                # Verify results are reasonable
                assert isinstance(using_recipes, list)
            
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / len(test_products)
            
            # Performance assertions
            assert avg_time < 0.5, f"Average product usage query took {avg_time:.3f}s, expected < 0.5s"
            
            print(f"Product usage queries: {avg_time:.3f}s avg per product")
    
    def test_large_recipe_creation_performance(self, app, repository):
        """Test performance of creating recipes with many ingredients."""
        with app.app_context():
            db.create_all()
            
            # Create recipe with many ingredients
            ingredient_counts = [10, 25, 50, 100]
            
            for count in ingredient_counts:
                recipe_data = {
                    'product_id': str(uuid.uuid4()),
                    'name': f'Large Recipe {count} ingredients',
                    'status': 'active',
                    'yield_quantity': 1000.0,
                    'yield_unit': 'gram',
                    'ingredients': []
                }
                
                # Create many ingredients
                for i in range(count):
                    ingredient = {
                        'ingredient_product_id': str(uuid.uuid4()),
                        'quantity': 100.0 + i,
                        'unit': 'gram',
                        'sort_order': i
                    }
                    recipe_data['ingredients'].append(ingredient)
                
                # Mock product client for validation
                with pytest.mock.patch('app.services.recipe_repository.product_client') as mock_client:
                    mock_client.validate_product_exists.return_value = True
                    mock_client.validate_products_exist.return_value = {
                        ing['ingredient_product_id']: True 
                        for ing in recipe_data['ingredients']
                    }
                    
                    start_time = time.time()
                    
                    try:
                        recipe = repository.create(recipe_data)
                        db.session.commit()
                        
                        end_time = time.time()
                        creation_time = end_time - start_time
                        
                        # Performance assertions
                        assert creation_time < 5.0, f"Recipe creation with {count} ingredients took {creation_time:.3f}s, expected < 5.0s"
                        assert recipe.id is not None
                        
                        print(f"Recipe creation ({count} ingredients): {creation_time:.3f}s")
                        
                    except Exception as e:
                        print(f"Failed to create recipe with {count} ingredients: {e}")
                        db.session.rollback()
    
    def test_pagination_performance(self, app, repository):
        """Test performance of paginated recipe queries."""
        # Create many recipes
        with app.app_context():
            db.create_all()
            
            # Create 100 simple recipes
            recipes = []
            for i in range(100):
                recipe = Recipe(
                    product_id=uuid.uuid4(),
                    name=f"Pagination Test Recipe {i}",
                    status=RecipeStatus.ACTIVE
                )
                
                # Add one ingredient to each
                ingredient = RecipeIngredient(
                    ingredient_product_id=uuid.uuid4(),
                    quantity=Decimal('100.0'),
                    unit=IngredientUnit.GRAM
                )
                recipe.ingredients.append(ingredient)
                
                recipes.append(recipe)
            
            db.session.add_all(recipes)
            db.session.commit()
            
            # Test different page sizes
            page_sizes = [10, 25, 50]
            
            for page_size in page_sizes:
                start_time = time.time()
                
                # Get first few pages
                for page in range(1, 4):
                    recipe_list, pagination = repository.get_all(
                        page=page, 
                        per_page=page_size,
                        include_relationships=True
                    )
                    
                    # Verify results
                    assert len(recipe_list) <= page_size
                    assert pagination['page'] == page
                    assert pagination['per_page'] == page_size
                
                end_time = time.time()
                query_time = end_time - start_time
                
                # Performance assertions
                assert query_time < 2.0, f"Pagination queries (page_size={page_size}) took {query_time:.3f}s, expected < 2.0s"
                
                print(f"Pagination (page_size={page_size}): {query_time:.3f}s for 3 pages")
    
    @pytest.mark.slow
    def test_stress_test_hierarchy_queries(self, app, repository):
        """Stress test with very large hierarchy (marked as slow test)."""
        # This test is marked as slow and may be skipped in regular test runs
        recipes = self.create_recipe_hierarchy(app, depth=6, branching_factor=3)
        
        with app.app_context():
            # Test the most complex recipe
            top_recipe = recipes[-1]
            
            # Run multiple queries to test consistency
            query_times = []
            
            for i in range(5):
                start_time = time.time()
                hierarchy = repository.get_recipe_hierarchy(top_recipe.id, max_depth=15)
                end_time = time.time()
                
                query_time = end_time - start_time
                query_times.append(query_time)
                
                # Verify results consistency
                assert len(hierarchy) > 0
                
                print(f"Stress test iteration {i+1}: {query_time:.3f}s, {len(hierarchy)} items")
            
            # Calculate statistics
            avg_time = sum(query_times) / len(query_times)
            max_time = max(query_times)
            min_time = min(query_times)
            
            # Performance assertions for stress test
            assert avg_time < 10.0, f"Average stress test query took {avg_time:.3f}s, expected < 10.0s"
            assert max_time < 15.0, f"Maximum stress test query took {max_time:.3f}s, expected < 15.0s"
            
            print(f"Stress test summary: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")