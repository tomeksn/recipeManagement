-- Migration: 003_initial_calculator_service.sql
-- Description: Initial migration for Calculator Service schema
-- Created: 2025-01-24
-- Author: System

-- Execute the calculator service schema
\i database/schemas/calculator-service-schema.sql

-- Insert sample calculation templates
INSERT INTO calculator_service.calculation_templates (name, description, calculation_type, template_parameters, default_values, validation_rules) VALUES
    (
        'Scale Recipe by Pieces',
        'Scale recipe ingredients based on target number of pieces',
        'scale_by_quantity',
        '{"target_pieces": {"type": "integer", "required": true}, "original_yield": {"type": "integer", "required": true}}',
        '{"target_pieces": 24, "original_yield": 12}',
        '{"target_pieces": {"min": 1, "max": 1000}, "original_yield": {"min": 1, "max": 1000}}'
    ),
    (
        'Scale Recipe by Weight',
        'Scale recipe ingredients based on target weight',
        'scale_by_weight',
        '{"target_weight": {"type": "decimal", "required": true}, "target_unit": {"type": "string", "required": true}, "original_weight": {"type": "decimal", "required": true}}',
        '{"target_weight": 1000, "target_unit": "gram", "original_weight": 500}',
        '{"target_weight": {"min": 0.1}, "original_weight": {"min": 0.1}}'
    ),
    (
        'Unit Conversion',
        'Convert ingredients between different units',
        'unit_conversion',
        '{"from_unit": {"type": "string", "required": true}, "to_unit": {"type": "string", "required": true}, "quantity": {"type": "decimal", "required": true}}',
        '{"from_unit": "gram", "to_unit": "kilogram", "quantity": 1000}',
        '{"quantity": {"min": 0.001}}'
    ),
    (
        'Nutritional Calculation',
        'Calculate nutritional information for scaled recipes',
        'nutritional',
        '{"serving_size": {"type": "decimal", "required": true}, "servings": {"type": "integer", "required": true}}',
        '{"serving_size": 100, "servings": 4}',
        '{"serving_size": {"min": 1}, "servings": {"min": 1, "max": 100}}'
    );

-- Insert sample performance metrics (for demonstration)
INSERT INTO calculator_service.calculation_performance_metrics (
    metric_date, 
    metric_hour, 
    total_calculations, 
    cached_calculations, 
    failed_calculations,
    avg_calculation_time_ms,
    min_calculation_time_ms,
    max_calculation_time_ms,
    cache_hit_rate
) VALUES
    (CURRENT_DATE, 10, 150, 45, 2, 25.50, 5, 120, 0.3000),
    (CURRENT_DATE, 11, 200, 80, 1, 22.75, 3, 95, 0.4000),
    (CURRENT_DATE, 12, 300, 180, 3, 18.25, 2, 150, 0.6000);

-- Insert migration tracking
INSERT INTO public.schema_migrations (version) VALUES ('003_initial_calculator_service');
