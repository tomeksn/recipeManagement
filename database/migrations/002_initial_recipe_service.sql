-- Migration: 002_initial_recipe_service.sql
-- Description: Initial migration for Recipe Service schema
-- Created: 2025-01-24
-- Author: System

-- Execute the recipe service schema
\i database/schemas/recipe-service-schema.sql

-- Insert sample recipes using product IDs
DO $$
DECLARE
    flour_id UUID;
    sugar_id UUID;
    butter_id UUID;
    eggs_id UUID;
    vanilla_id UUID;
    baking_powder_id UUID;
    chocolate_chips_id UUID;
    bread_dough_id UUID;
    cookie_mix_id UUID;
    
    cookie_recipe_id UUID;
    bread_recipe_id UUID;
BEGIN
    -- Get product IDs
    SELECT id INTO flour_id FROM product_service.products WHERE name = 'Flour';
    SELECT id INTO sugar_id FROM product_service.products WHERE name = 'Sugar';
    SELECT id INTO butter_id FROM product_service.products WHERE name = 'Butter';
    SELECT id INTO eggs_id FROM product_service.products WHERE name = 'Eggs';
    SELECT id INTO vanilla_id FROM product_service.products WHERE name = 'Vanilla Extract';
    SELECT id INTO baking_powder_id FROM product_service.products WHERE name = 'Baking Powder';
    SELECT id INTO chocolate_chips_id FROM product_service.products WHERE name = 'Chocolate Chips';
    SELECT id INTO bread_dough_id FROM product_service.products WHERE name = 'Bread Dough';
    SELECT id INTO cookie_mix_id FROM product_service.products WHERE name = 'Cookie Mix';
    
    -- Create Chocolate Chip Cookie recipe
    INSERT INTO recipe_service.recipes (product_id, name, description, status, yield_quantity, yield_unit, preparation_time)
    VALUES (cookie_mix_id, 'Chocolate Chip Cookies', 'Classic homemade chocolate chip cookies', 'active', 24, 'piece', 45)
    RETURNING id INTO cookie_recipe_id;
    
    -- Add ingredients for cookie recipe
    INSERT INTO recipe_service.recipe_ingredients (recipe_id, ingredient_product_id, quantity, unit, sort_order, ingredient_group) VALUES
        (cookie_recipe_id, flour_id, 250, 'gram', 1, 'Dry Ingredients'),
        (cookie_recipe_id, sugar_id, 150, 'gram', 2, 'Dry Ingredients'),
        (cookie_recipe_id, baking_powder_id, 5, 'gram', 3, 'Dry Ingredients'),
        (cookie_recipe_id, butter_id, 125, 'gram', 4, 'Wet Ingredients'),
        (cookie_recipe_id, eggs_id, 1, 'piece', 5, 'Wet Ingredients'),
        (cookie_recipe_id, vanilla_id, 5, 'gram', 6, 'Wet Ingredients'),
        (cookie_recipe_id, chocolate_chips_id, 200, 'gram', 7, 'Mix-ins');
    
    -- Create Simple Bread recipe
    INSERT INTO recipe_service.recipes (product_id, name, description, status, yield_quantity, yield_unit, preparation_time)
    VALUES (bread_dough_id, 'Simple White Bread', 'Basic white bread recipe', 'active', 1, 'piece', 180)
    RETURNING id INTO bread_recipe_id;
    
    -- Add ingredients for bread recipe
    INSERT INTO recipe_service.recipe_ingredients (recipe_id, ingredient_product_id, quantity, unit, sort_order, ingredient_group) VALUES
        (bread_recipe_id, flour_id, 500, 'gram', 1, 'Base'),
        (bread_recipe_id, sugar_id, 25, 'gram', 2, 'Base'),
        (bread_recipe_id, butter_id, 50, 'gram', 3, 'Enrichment');
    
    -- Create recipe dependencies
    INSERT INTO recipe_service.recipe_dependencies (parent_recipe_id, child_product_id, dependency_type, depth_level) VALUES
        (cookie_recipe_id, flour_id, 'ingredient', 1),
        (cookie_recipe_id, sugar_id, 'ingredient', 1),
        (cookie_recipe_id, butter_id, 'ingredient', 1),
        (bread_recipe_id, flour_id, 'ingredient', 1),
        (bread_recipe_id, sugar_id, 'ingredient', 1);
END $$;

-- Insert sample recipe tags
INSERT INTO recipe_service.recipe_tags (name, color, description) VALUES
    ('dessert', '#FF69B4', 'Sweet dessert recipes'),
    ('bread', '#DEB887', 'Bread and baked goods'),
    ('quick', '#90EE90', 'Quick preparation recipes'),
    ('family-friendly', '#87CEEB', 'Great for families'),
    ('traditional', '#D2691E', 'Traditional recipes');

-- Insert migration tracking
INSERT INTO public.schema_migrations (version) VALUES ('002_initial_recipe_service');
