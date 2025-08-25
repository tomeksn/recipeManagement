"""Unit tests for CalculationService."""
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.services.calculation_service import CalculationService
from app.utils.exceptions import (
    CalculationError, InvalidScaleFactorError, RecipeNotFoundError,
    InvalidInputError, MaxIngredientsExceededError
)


class TestCalculationService:
    """Test cases for CalculationService."""
    
    @pytest.fixture
    def service(self, app_context):
        """Create calculation service instance."""
        return CalculationService()
    
    def test_round_quantity_pieces(self, service):
        """Test quantity rounding for pieces."""
        # Whole numbers for quantities >= 1
        assert service._round_quantity(1.4, 'piece') == 1.0
        assert service._round_quantity(1.5, 'piece') == 2.0
        assert service._round_quantity(10.7, 'piece') == 11.0
        
        # One decimal place for quantities < 1
        assert service._round_quantity(0.14, 'piece') == 0.1
        assert service._round_quantity(0.15, 'piece') == 0.2
        assert service._round_quantity(0.74, 'piece') == 0.7
    
    def test_round_quantity_grams(self, service):
        """Test quantity rounding for grams."""
        # Default 3 decimal places
        assert service._round_quantity(123.4567, 'gram') == 123.457
        assert service._round_quantity(123.4564, 'gram') == 123.456
        
        # Custom precision
        assert service._round_quantity(123.4567, 'gram', precision=2) == 123.46
        assert service._round_quantity(123.4567, 'gram', precision=0) == 123.0
    
    def test_validate_scale_factor_valid(self, service):
        """Test valid scale factor validation."""
        # Should not raise exception
        service._validate_scale_factor(1.0)
        service._validate_scale_factor(0.5)
        service._validate_scale_factor(2.0)
        service._validate_scale_factor(100.0)
    
    def test_validate_scale_factor_invalid(self, service):
        """Test invalid scale factor validation."""
        with pytest.raises(InvalidScaleFactorError):
            service._validate_scale_factor(0)
        
        with pytest.raises(InvalidScaleFactorError):
            service._validate_scale_factor(-1)
        
        with pytest.raises(InvalidScaleFactorError):
            service._validate_scale_factor(1001)  # Exceeds max
        
        with pytest.raises(InvalidScaleFactorError):
            service._validate_scale_factor(0.0001)  # Below min
    
    def test_calculate_scale_factor_valid(self, service):
        """Test valid scale factor calculation."""
        # Same units, different quantities
        factor = service._calculate_scale_factor(24, 'piece', 100, 'piece')
        assert abs(factor - 4.166666666666667) < 0.000001
        
        factor = service._calculate_scale_factor(1000, 'gram', 500, 'gram')
        assert factor == 0.5
    
    def test_calculate_scale_factor_mismatched_units(self, service):
        """Test scale factor calculation with mismatched units."""
        with pytest.raises(InvalidInputError):
            service._calculate_scale_factor(24, 'piece', 100, 'gram')
    
    def test_calculate_scale_factor_invalid_quantities(self, service):
        """Test scale factor calculation with invalid quantities."""
        with pytest.raises(InvalidInputError):
            service._calculate_scale_factor(0, 'piece', 100, 'piece')
        
        with pytest.raises(InvalidInputError):
            service._calculate_scale_factor(24, 'piece', -5, 'piece')
    
    def test_scale_ingredient(self, service):
        """Test individual ingredient scaling."""
        ingredient = {
            'product_id': '660e8400-e29b-41d4-a716-446655440001',
            'product_name': 'Flour',
            'quantity': 500,
            'unit': 'gram',
            'order': 1
        }
        
        scaled = service._scale_ingredient(ingredient, 2.0)
        
        assert scaled['product_id'] == ingredient['product_id']
        assert scaled['product_name'] == 'Flour'
        assert scaled['original_quantity'] == 500
        assert scaled['calculated_quantity'] == 1000.0
        assert scaled['unit'] == 'gram'
        assert scaled['order'] == 1
    
    def test_scale_ingredient_pieces(self, service):
        """Test ingredient scaling for pieces."""
        ingredient = {
            'product_id': '660e8400-e29b-41d4-a716-446655440004',
            'product_name': 'Eggs',
            'quantity': 2,
            'unit': 'piece',
            'order': 4
        }
        
        scaled = service._scale_ingredient(ingredient, 4.17)
        
        assert scaled['calculated_quantity'] == 8.0  # Rounded to whole number
        assert scaled['unit'] == 'piece'
    
    def test_scale_recipe_ingredients(self, service, sample_recipe_data):
        """Test scaling all ingredients in a recipe."""
        scaled_ingredients = service._scale_recipe_ingredients(
            sample_recipe_data, 2.0
        )
        
        assert len(scaled_ingredients) == 4
        
        # Check flour (gram ingredient)
        flour = next(i for i in scaled_ingredients if i['product_name'] == 'Flour')
        assert flour['calculated_quantity'] == 1000.0
        
        # Check eggs (piece ingredient)
        eggs = next(i for i in scaled_ingredients if i['product_name'] == 'Eggs')
        assert eggs['calculated_quantity'] == 4.0
    
    def test_scale_recipe_ingredients_max_exceeded(self, service):
        """Test scaling recipe with too many ingredients."""
        # Create recipe with too many ingredients
        large_recipe = {
            'ingredients': [
                {
                    'product_id': f'id-{i}',
                    'product_name': f'Ingredient {i}',
                    'quantity': 100,
                    'unit': 'gram',
                    'order': i
                }
                for i in range(1001)  # Exceeds max_ingredients
            ]
        }
        
        with pytest.raises(MaxIngredientsExceededError):
            service._scale_recipe_ingredients(large_recipe, 1.0)
    
    @patch('app.services.calculation_service.recipe_client')
    def test_calculate_recipe_basic(self, mock_client, service, sample_recipe_data):
        """Test basic recipe calculation."""
        mock_client.get_recipe.return_value = sample_recipe_data
        
        result = service.calculate_recipe(
            product_id='550e8400-e29b-41d4-a716-446655440000',
            target_quantity=100,
            target_unit='piece'
        )
        
        assert result['product_id'] == '550e8400-e29b-41d4-a716-446655440000'
        assert result['target_quantity'] == 100
        assert result['target_unit'] == 'piece'
        assert abs(result['scale_factor'] - 4.166666666666667) < 0.000001
        assert len(result['ingredients']) == 4
        assert result['cached'] is False
        assert 'calculation_time_ms' in result
    
    @patch('app.services.calculation_service.recipe_client')
    def test_calculate_recipe_not_found(self, mock_client, service):
        """Test calculation when recipe not found."""
        mock_client.get_recipe.return_value = None
        
        with pytest.raises(RecipeNotFoundError):
            service.calculate_recipe(
                product_id='nonexistent-id',
                target_quantity=100,
                target_unit='piece'
            )
    
    @patch('app.services.calculation_service.recipe_client')
    def test_calculate_recipe_gram_based(self, mock_client, service):
        """Test calculation for gram-based recipe."""
        gram_recipe = {
            'id': '770e8400-e29b-41d4-a716-446655440000',
            'product': {
                'id': '770e8400-e29b-41d4-a716-446655440000',
                'name': 'Cake Batter',
                'type': 'standard',
                'unit': 'gram'
            },
            'yield_quantity': 1000,
            'yield_unit': 'gram',
            'ingredients': [
                {
                    'product_id': '660e8400-e29b-41d4-a716-446655440001',
                    'product_name': 'Flour',
                    'quantity': 600,
                    'unit': 'gram',
                    'order': 1
                },
                {
                    'product_id': '660e8400-e29b-41d4-a716-446655440002',
                    'product_name': 'Sugar',
                    'quantity': 400,
                    'unit': 'gram',
                    'order': 2
                }
            ]
        }
        
        mock_client.get_recipe.return_value = gram_recipe
        
        result = service.calculate_recipe(
            product_id='770e8400-e29b-41d4-a716-446655440000',
            target_quantity=500,
            target_unit='gram'
        )
        
        assert result['scale_factor'] == 0.5
        
        # Check scaled ingredients
        flour = next(i for i in result['ingredients'] if i['product_name'] == 'Flour')
        assert flour['calculated_quantity'] == 300.0
        
        sugar = next(i for i in result['ingredients'] if i['product_name'] == 'Sugar')
        assert sugar['calculated_quantity'] == 200.0
    
    @patch('app.services.calculation_service.recipe_client')
    def test_calculate_batch(self, mock_client, service, sample_recipe_data):
        """Test batch calculation."""
        mock_client.get_recipe.return_value = sample_recipe_data
        
        calculations = [
            {
                'product_id': '550e8400-e29b-41d4-a716-446655440000',
                'target_quantity': 100,
                'target_unit': 'piece'
            },
            {
                'product_id': '550e8400-e29b-41d4-a716-446655440000',
                'target_quantity': 50,
                'target_unit': 'piece'
            }
        ]
        
        result = service.calculate_batch(calculations)
        
        assert result['summary']['total_requests'] == 2
        assert result['summary']['successful'] == 2
        assert result['summary']['failed'] == 0
        assert len(result['results']) == 2
        assert result['summary']['total_time_ms'] > 0
    
    @patch('app.services.calculation_service.recipe_client')
    def test_calculate_batch_with_errors(self, mock_client, service):
        """Test batch calculation with some failures."""
        # First call succeeds, second fails
        mock_client.get_recipe.side_effect = [
            {
                'id': '550e8400-e29b-41d4-a716-446655440000',
                'product': {'name': 'Test'},
                'yield_quantity': 24,
                'yield_unit': 'piece',
                'ingredients': []
            },
            None  # Recipe not found
        ]
        
        calculations = [
            {
                'product_id': '550e8400-e29b-41d4-a716-446655440000',
                'target_quantity': 100,
                'target_unit': 'piece'
            },
            {
                'product_id': 'nonexistent-id',
                'target_quantity': 50,
                'target_unit': 'piece'
            }
        ]
        
        result = service.calculate_batch(calculations)
        
        assert result['summary']['total_requests'] == 2
        assert result['summary']['successful'] == 1
        assert result['summary']['failed'] == 1
        assert len(result['results']) == 1
        assert len(result['summary']['errors']) == 1
    
    def test_cache_key_generation(self, service):
        """Test cache key generation."""
        key1 = service._generate_cache_key(
            'product-1', 100, 'piece', False, 5
        )
        key2 = service._generate_cache_key(
            'product-1', 100, 'piece', False, 5
        )
        key3 = service._generate_cache_key(
            'product-1', 200, 'piece', False, 5
        )
        
        # Same parameters should generate same key
        assert key1 == key2
        
        # Different parameters should generate different key
        assert key1 != key3
        
        # Key should start with 'calc:'
        assert key1.startswith('calc:')


class TestCalculationServiceEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def service(self, app_context):
        """Create calculation service instance."""
        return CalculationService()
    
    def test_very_small_quantities(self, service):
        """Test calculation with very small quantities."""
        ingredient = {
            'product_id': 'test-id',
            'product_name': 'Test',
            'quantity': 0.001,
            'unit': 'gram',
            'order': 1
        }
        
        scaled = service._scale_ingredient(ingredient, 0.5)
        assert scaled['calculated_quantity'] == 0.001  # Minimum precision
    
    def test_very_large_quantities(self, service):
        """Test calculation with large quantities."""
        ingredient = {
            'product_id': 'test-id',
            'product_name': 'Test',
            'quantity': 999999,
            'unit': 'gram',
            'order': 1
        }
        
        scaled = service._scale_ingredient(ingredient, 2.0)
        assert scaled['calculated_quantity'] == 1999998.0
    
    def test_precision_edge_cases(self, service):
        """Test precision handling edge cases."""
        # Test precision 0 (whole numbers)
        assert service._round_quantity(123.456, 'gram', precision=0) == 123.0
        
        # Test precision 6 (maximum)
        assert service._round_quantity(123.456789123, 'gram', precision=6) == 123.456789
    
    def test_decimal_precision(self, service):
        """Test Decimal precision in calculations."""
        # Use Decimal to avoid floating point precision issues
        ingredient = {
            'product_id': 'test-id',
            'product_name': 'Test',
            'quantity': Decimal('0.1'),
            'unit': 'gram',
            'order': 1
        }
        
        scaled = service._scale_ingredient(ingredient, Decimal('3'))
        assert scaled['calculated_quantity'] == 0.3