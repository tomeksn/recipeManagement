-- Migration: 004_enhance_recipe_hierarchy.sql
-- Description: Enhance recipe hierarchy functionality with better performance
-- Created: 2025-01-24
-- Author: System

-- Set search path for this session
SET search_path TO recipe_service, public;

-- Drop existing function and recreate with improvements
DROP FUNCTION IF EXISTS calculate_recipe_hierarchy(UUID);

-- Enhanced function to calculate recipe hierarchy with better product handling
CREATE OR REPLACE FUNCTION calculate_recipe_hierarchy(recipe_uuid UUID)
RETURNS TABLE (
    ingredient_product_id UUID,
    ingredient_name TEXT,
    quantity DECIMAL(10,3),
    unit ingredient_unit,
    depth_level INTEGER,
    path TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE recipe_hierarchy AS (
        -- Base case: direct ingredients
        SELECT 
            ri.ingredient_product_id,
            COALESCE(
                'Product_' || ri.ingredient_product_id::TEXT,
                ri.ingredient_product_id::TEXT
            ) as ingredient_name,
            ri.quantity,
            ri.unit,
            1 as depth_level,
            ARRAY[ri.ingredient_product_id::TEXT] as path
        FROM recipe_ingredients ri
        WHERE ri.recipe_id = recipe_uuid
        
        UNION ALL
        
        -- Recursive case: ingredients of sub-recipes
        SELECT 
            ri.ingredient_product_id,
            COALESCE(
                'Product_' || ri.ingredient_product_id::TEXT,
                ri.ingredient_product_id::TEXT
            ),
            -- Scale quantities based on parent requirement
            ROUND((ri.quantity * rh.quantity)::DECIMAL, 3) as quantity,
            ri.unit,
            rh.depth_level + 1,
            rh.path || ri.ingredient_product_id::TEXT
        FROM recipe_ingredients ri
        JOIN recipes r ON r.product_id = rh.ingredient_product_id
        JOIN recipe_hierarchy rh ON r.id != recipe_uuid -- Prevent cycles
        WHERE rh.depth_level < 10 -- Limit recursion depth
        AND NOT (ri.ingredient_product_id::TEXT = ANY(rh.path)) -- Prevent cycles
        AND r.status = 'active' -- Only include active recipes
    )
    SELECT 
        rh.ingredient_product_id,
        rh.ingredient_name,
        rh.quantity,
        rh.unit,
        rh.depth_level,
        rh.path
    FROM recipe_hierarchy rh
    ORDER BY rh.depth_level, rh.ingredient_name;
END;
$$ LANGUAGE plpgsql;

-- Create optimized function for recipe complexity analysis
CREATE OR REPLACE FUNCTION analyze_recipe_complexity(recipe_uuid UUID)
RETURNS TABLE (
    metric_name TEXT,
    metric_value DECIMAL,
    metric_description TEXT
) AS $$
DECLARE
    ingredient_count INTEGER := 0;
    hierarchy_depth INTEGER := 0;
    total_expanded INTEGER := 0;
    optional_count INTEGER := 0;
    group_count INTEGER := 0;
BEGIN
    -- Get basic ingredient count
    SELECT COUNT(*) INTO ingredient_count
    FROM recipe_ingredients
    WHERE recipe_id = recipe_uuid;
    
    -- Get optional ingredient count
    SELECT COUNT(*) INTO optional_count
    FROM recipe_ingredients
    WHERE recipe_id = recipe_uuid AND is_optional = true;
    
    -- Get ingredient group count
    SELECT COUNT(DISTINCT ingredient_group) INTO group_count
    FROM recipe_ingredients
    WHERE recipe_id = recipe_uuid AND ingredient_group IS NOT NULL;
    
    -- Get hierarchy metrics
    SELECT 
        COALESCE(MAX(depth_level), 1),
        COUNT(*)
    INTO hierarchy_depth, total_expanded
    FROM calculate_recipe_hierarchy(recipe_uuid);
    
    -- Return metrics
    RETURN QUERY VALUES
        ('ingredient_count', ingredient_count::DECIMAL, 'Direct ingredients in recipe'),
        ('hierarchy_depth', hierarchy_depth::DECIMAL, 'Maximum depth of ingredient hierarchy'),
        ('total_expanded', total_expanded::DECIMAL, 'Total ingredients when fully expanded'),
        ('optional_count', optional_count::DECIMAL, 'Number of optional ingredients'),
        ('group_count', group_count::DECIMAL, 'Number of ingredient groups');
END;
$$ LANGUAGE plpgsql;

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_composite 
ON recipe_ingredients(recipe_id, ingredient_product_id, is_optional);

CREATE INDEX IF NOT EXISTS idx_recipes_product_status 
ON recipes(product_id, status) WHERE status = 'active';

-- Grant permissions
GRANT EXECUTE ON FUNCTION calculate_recipe_hierarchy(UUID) TO recipe_user;
GRANT EXECUTE ON FUNCTION analyze_recipe_complexity(UUID) TO recipe_user;

-- Insert migration tracking
INSERT INTO public.schema_migrations (version) VALUES ('004_enhance_recipe_hierarchy');