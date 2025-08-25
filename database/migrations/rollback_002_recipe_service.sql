-- Rollback Migration: 002_initial_recipe_service.sql
-- Description: Rollback script for Recipe Service schema
-- Created: 2025-01-24
-- Author: System

-- Remove migration tracking
DELETE FROM public.schema_migrations WHERE version = '002_initial_recipe_service';

-- Drop all recipe service tables in reverse dependency order
DROP TRIGGER IF EXISTS prevent_circular_dependencies ON recipe_service.recipe_dependencies;
DROP TRIGGER IF EXISTS update_recipe_ingredients_updated_at ON recipe_service.recipe_ingredients;
DROP TRIGGER IF EXISTS update_recipes_updated_at ON recipe_service.recipes;

DROP FUNCTION IF EXISTS recipe_service.check_circular_dependency();
DROP FUNCTION IF EXISTS recipe_service.update_updated_at_column();
DROP FUNCTION IF EXISTS recipe_service.calculate_recipe_hierarchy(UUID);
DROP FUNCTION IF EXISTS recipe_service.validate_recipe(UUID);

DROP TABLE IF EXISTS recipe_service.recipe_audit;
DROP TABLE IF EXISTS recipe_service.recipe_tag_assignments;
DROP TABLE IF EXISTS recipe_service.recipe_tags;
DROP TABLE IF EXISTS recipe_service.recipe_nutrition;
DROP TABLE IF EXISTS recipe_service.recipe_dependencies;
DROP TABLE IF EXISTS recipe_service.recipe_versions;
DROP TABLE IF EXISTS recipe_service.recipe_ingredients;
DROP TABLE IF EXISTS recipe_service.recipes;

DROP TYPE IF EXISTS recipe_service.ingredient_unit;
DROP TYPE IF EXISTS recipe_service.recipe_status;

-- Revoke permissions
REVOKE ALL PRIVILEGES ON SCHEMA recipe_service FROM recipe_user;
REVOKE USAGE ON SCHEMA recipe_service FROM recipe_user;

-- Drop schema
DROP SCHEMA IF EXISTS recipe_service CASCADE;
