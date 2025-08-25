-- Recipe Service Database Schema
-- This file defines the complete database schema for the Recipe Service

-- Create the recipe_service schema
CREATE SCHEMA IF NOT EXISTS recipe_service;

-- Set search path for this session
SET search_path TO recipe_service, public;

-- Create ENUM types for recipe management
CREATE TYPE recipe_status AS ENUM ('draft', 'active', 'archived', 'deprecated');
CREATE TYPE ingredient_unit AS ENUM ('piece', 'gram', 'milliliter', 'liter', 'kilogram');

-- Create recipes table
CREATE TABLE recipes (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Product relationship
    product_id UUID NOT NULL, -- References product_service.products(id)
    
    -- Recipe information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    status recipe_status NOT NULL DEFAULT 'draft',
    
    -- Recipe metadata
    yield_quantity DECIMAL(10,3), -- Expected yield quantity
    yield_unit ingredient_unit, -- Unit for yield
    preparation_time INTEGER, -- Preparation time in minutes
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID, -- Reference to user who created the recipe
    updated_by UUID, -- Reference to user who last updated the recipe
    
    -- Business constraints
    CONSTRAINT recipes_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT recipes_version_positive CHECK (version > 0),
    CONSTRAINT recipes_yield_quantity_positive CHECK (yield_quantity IS NULL OR yield_quantity > 0),
    CONSTRAINT recipes_preparation_time_positive CHECK (preparation_time IS NULL OR preparation_time > 0),
    
    -- Unique constraint for product-version combination
    UNIQUE (product_id, version)
);

-- Create indexes for recipes
CREATE INDEX idx_recipes_product_id ON recipes(product_id);
CREATE INDEX idx_recipes_status ON recipes(status);
CREATE INDEX idx_recipes_version ON recipes(version);
CREATE INDEX idx_recipes_created_at ON recipes(created_at);
CREATE INDEX idx_recipes_updated_at ON recipes(updated_at);
CREATE INDEX idx_recipes_name ON recipes(name);

-- Create recipe_ingredients table
CREATE TABLE recipe_ingredients (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Recipe relationship
    recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    
    -- Ingredient information
    ingredient_product_id UUID NOT NULL, -- References product_service.products(id)
    quantity DECIMAL(10,3) NOT NULL,
    unit ingredient_unit NOT NULL,
    
    -- Ordering and organization
    sort_order INTEGER NOT NULL DEFAULT 0,
    ingredient_group VARCHAR(100), -- Optional grouping (e.g., "Base", "Seasoning")
    
    -- Additional metadata
    notes TEXT,
    is_optional BOOLEAN NOT NULL DEFAULT FALSE,
    substitute_ingredients JSONB, -- Array of alternative ingredient IDs
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Business constraints
    CONSTRAINT recipe_ingredients_quantity_positive CHECK (quantity > 0),
    CONSTRAINT recipe_ingredients_sort_order_non_negative CHECK (sort_order >= 0),
    
    -- Unique constraint to prevent duplicate ingredients in same recipe
    UNIQUE (recipe_id, ingredient_product_id)
);

-- Create indexes for recipe_ingredients
CREATE INDEX idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_ingredient_product_id ON recipe_ingredients(ingredient_product_id);
CREATE INDEX idx_recipe_ingredients_sort_order ON recipe_ingredients(sort_order);
CREATE INDEX idx_recipe_ingredients_group ON recipe_ingredients(ingredient_group);

-- Create recipe_versions table for version history
CREATE TABLE recipe_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    recipe_data JSONB NOT NULL, -- Complete recipe snapshot
    change_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID,
    
    UNIQUE (recipe_id, version_number)
);

-- Create index for recipe versions
CREATE INDEX idx_recipe_versions_recipe_id ON recipe_versions(recipe_id);
CREATE INDEX idx_recipe_versions_version_number ON recipe_versions(version_number);
CREATE INDEX idx_recipe_versions_created_at ON recipe_versions(created_at);

-- Create recipe_dependencies table for tracking hierarchical relationships
CREATE TABLE recipe_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    child_product_id UUID NOT NULL, -- Product that is used as ingredient
    dependency_type VARCHAR(50) NOT NULL DEFAULT 'ingredient', -- ingredient, sub-recipe, etc.
    depth_level INTEGER NOT NULL DEFAULT 1, -- How deep in the hierarchy
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Prevent circular dependencies
    CONSTRAINT recipe_dependencies_no_self_reference 
        CHECK (parent_recipe_id != child_product_id::UUID),
    
    UNIQUE (parent_recipe_id, child_product_id)
);

-- Create indexes for recipe dependencies
CREATE INDEX idx_recipe_dependencies_parent ON recipe_dependencies(parent_recipe_id);
CREATE INDEX idx_recipe_dependencies_child ON recipe_dependencies(child_product_id);
CREATE INDEX idx_recipe_dependencies_depth ON recipe_dependencies(depth_level);

-- Create recipe_nutrition table for nutritional information
CREATE TABLE recipe_nutrition (
    recipe_id UUID PRIMARY KEY REFERENCES recipes(id) ON DELETE CASCADE,
    
    -- Macronutrients per 100g/100ml
    calories DECIMAL(8,2),
    protein DECIMAL(8,2),
    carbohydrates DECIMAL(8,2),
    fat DECIMAL(8,2),
    fiber DECIMAL(8,2),
    sugar DECIMAL(8,2),
    sodium DECIMAL(8,2),
    
    -- Calculation metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    calculation_method VARCHAR(100), -- 'manual', 'automated', 'imported'
    
    -- Constraints
    CONSTRAINT recipe_nutrition_values_non_negative CHECK (
        (calories IS NULL OR calories >= 0) AND
        (protein IS NULL OR protein >= 0) AND
        (carbohydrates IS NULL OR carbohydrates >= 0) AND
        (fat IS NULL OR fat >= 0) AND
        (fiber IS NULL OR fiber >= 0) AND
        (sugar IS NULL OR sugar >= 0) AND
        (sodium IS NULL OR sodium >= 0)
    )
);

-- Create recipe_tags table for flexible tagging
CREATE TABLE recipe_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7), -- Hex color code
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT recipe_tags_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT recipe_tags_color_format CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Create recipe_tag_assignments table
CREATE TABLE recipe_tag_assignments (
    recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES recipe_tags(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    PRIMARY KEY (recipe_id, tag_id)
);

-- Create recipe_audit table for comprehensive change tracking
CREATE TABLE recipe_audit (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID NOT NULL,
    ingredient_id UUID, -- NULL for recipe-level changes
    operation VARCHAR(20) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT recipe_audit_operation_check CHECK (
        operation IN ('INSERT', 'UPDATE', 'DELETE', 'VERSION_CREATE')
    )
);

-- Create indexes for audit table
CREATE INDEX idx_recipe_audit_recipe_id ON recipe_audit(recipe_id);
CREATE INDEX idx_recipe_audit_changed_at ON recipe_audit(changed_at);
CREATE INDEX idx_recipe_audit_operation ON recipe_audit(operation);

-- Create functions for updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_recipes_updated_at 
    BEFORE UPDATE ON recipes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recipe_ingredients_updated_at 
    BEFORE UPDATE ON recipe_ingredients 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to prevent circular dependencies
CREATE OR REPLACE FUNCTION check_circular_dependency()
RETURNS TRIGGER AS $$
DECLARE
    circular_found BOOLEAN := FALSE;
BEGIN
    -- Check if adding this dependency would create a circular reference
    WITH RECURSIVE dependency_tree AS (
        -- Start with the new dependency
        SELECT 
            NEW.parent_recipe_id as recipe_id,
            NEW.child_product_id as product_id,
            1 as depth
        
        UNION ALL
        
        -- Recursively find all dependencies
        SELECT 
            rd.parent_recipe_id,
            rd.child_product_id,
            dt.depth + 1
        FROM recipe_dependencies rd
        JOIN dependency_tree dt ON rd.parent_recipe_id::TEXT = dt.product_id::TEXT
        WHERE dt.depth < 10 -- Prevent infinite recursion
    )
    SELECT TRUE INTO circular_found
    FROM dependency_tree
    WHERE recipe_id::TEXT = product_id::TEXT
    LIMIT 1;
    
    IF circular_found THEN
        RAISE EXCEPTION 'Circular dependency detected: Cannot add ingredient that would create a cycle';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to prevent circular dependencies
CREATE TRIGGER prevent_circular_dependencies
    BEFORE INSERT OR UPDATE ON recipe_dependencies
    FOR EACH ROW
    EXECUTE FUNCTION check_circular_dependency();

-- Create function to calculate recipe hierarchy depth
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
            ri.ingredient_product_id::TEXT as ingredient_name,
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
            ri.ingredient_product_id::TEXT,
            (ri.quantity * rh.quantity) as quantity, -- Scale quantities
            ri.unit,
            rh.depth_level + 1,
            rh.path || ri.ingredient_product_id::TEXT
        FROM recipe_ingredients ri
        JOIN recipes r ON r.product_id = rh.ingredient_product_id
        JOIN recipe_hierarchy rh ON r.id != recipe_uuid -- Prevent cycles
        WHERE rh.depth_level < 5 -- Limit recursion depth
        AND NOT (ri.ingredient_product_id::TEXT = ANY(rh.path)) -- Prevent cycles
    )
    SELECT * FROM recipe_hierarchy
    ORDER BY depth_level, ingredient_name;
END;
$$ LANGUAGE plpgsql;

-- Create function for recipe validation
CREATE OR REPLACE FUNCTION validate_recipe(recipe_uuid UUID)
RETURNS TABLE (
    is_valid BOOLEAN,
    validation_errors TEXT[]
) AS $$
DECLARE
    error_list TEXT[] := '{}';
    ingredient_count INTEGER;
    has_circular_deps BOOLEAN := FALSE;
BEGIN
    -- Check if recipe has at least one ingredient
    SELECT COUNT(*) INTO ingredient_count
    FROM recipe_ingredients
    WHERE recipe_id = recipe_uuid;
    
    IF ingredient_count = 0 THEN
        error_list := array_append(error_list, 'Recipe must have at least one ingredient');
    END IF;
    
    -- Check for circular dependencies
    SELECT EXISTS(
        SELECT 1 FROM recipe_dependencies
        WHERE parent_recipe_id = recipe_uuid
        AND child_product_id::UUID = recipe_uuid
    ) INTO has_circular_deps;
    
    IF has_circular_deps THEN
        error_list := array_append(error_list, 'Recipe contains circular dependencies');
    END IF;
    
    -- Return validation result
    RETURN QUERY SELECT 
        (array_length(error_list, 1) IS NULL OR array_length(error_list, 1) = 0) as is_valid,
        error_list as validation_errors;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT USAGE ON SCHEMA recipe_service TO recipe_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA recipe_service TO recipe_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA recipe_service TO recipe_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA recipe_service TO recipe_user;

-- Add comments for documentation
COMMENT ON SCHEMA recipe_service IS 'Schema for the Recipe Service microservice';
COMMENT ON TABLE recipes IS 'Main recipes table storing recipe information';
COMMENT ON TABLE recipe_ingredients IS 'Ingredients that make up each recipe';
COMMENT ON TABLE recipe_versions IS 'Version history for recipes';
COMMENT ON TABLE recipe_dependencies IS 'Hierarchical relationships between recipes';
COMMENT ON TABLE recipe_nutrition IS 'Nutritional information for recipes';
COMMENT ON TABLE recipe_audit IS 'Comprehensive audit trail for all recipe changes';

COMMENT ON COLUMN recipes.product_id IS 'References the product this recipe produces';
COMMENT ON COLUMN recipes.version IS 'Version number for recipe versioning';
COMMENT ON COLUMN recipes.status IS 'Current status of the recipe';
COMMENT ON COLUMN recipe_ingredients.quantity IS 'Amount of ingredient needed';
COMMENT ON COLUMN recipe_ingredients.sort_order IS 'Display order of ingredients';
COMMENT ON COLUMN recipe_ingredients.is_optional IS 'Whether ingredient is optional';

-- Reset search path
RESET search_path;
