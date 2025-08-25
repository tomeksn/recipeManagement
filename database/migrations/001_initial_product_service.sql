-- Migration: 001_initial_product_service.sql
-- Description: Initial migration for Product Service schema
-- Created: 2025-01-24
-- Author: System

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Execute the product service schema
\i database/schemas/product-service-schema.sql

-- Insert sample data for development
INSERT INTO product_service.products (name, type, unit, description) VALUES
    ('Flour', 'standard', 'gram', 'All-purpose wheat flour'),
    ('Sugar', 'standard', 'gram', 'White granulated sugar'),
    ('Salt', 'standard', 'gram', 'Table salt'),
    ('Butter', 'standard', 'gram', 'Unsalted butter'),
    ('Eggs', 'standard', 'piece', 'Large chicken eggs'),
    ('Milk', 'standard', 'gram', 'Whole milk'),
    ('Vanilla Extract', 'standard', 'gram', 'Pure vanilla extract'),
    ('Baking Powder', 'standard', 'gram', 'Double-acting baking powder'),
    ('Chocolate Chips', 'standard', 'gram', 'Semi-sweet chocolate chips'),
    ('Bread Dough', 'semi-product', 'gram', 'Basic bread dough mix'),
    ('Cookie Mix', 'kit', 'gram', 'Pre-mixed cookie ingredients'),
    ('Cake Batter', 'semi-product', 'gram', 'Basic vanilla cake batter');

-- Insert sample categories
INSERT INTO product_service.product_categories (name, description, color) VALUES
    ('Baking Ingredients', 'Basic ingredients for baking', '#FF6B6B'),
    ('Dairy Products', 'Milk, butter, cheese products', '#4ECDC4'),
    ('Dry Goods', 'Flour, sugar, spices', '#45B7D1'),
    ('Semi-Products', 'Intermediate processing products', '#96CEB4'),
    ('Kits', 'Pre-assembled ingredient kits', '#FFEAA7');

-- Insert sample tags
INSERT INTO product_service.product_tags (name) VALUES
    ('gluten-free'),
    ('organic'),
    ('bulk'),
    ('perishable'),
    ('allergen');

-- Create some category assignments
WITH flour_product AS (SELECT id FROM product_service.products WHERE name = 'Flour'),
     baking_category AS (SELECT id FROM product_service.product_categories WHERE name = 'Baking Ingredients'),
     dry_goods_category AS (SELECT id FROM product_service.product_categories WHERE name = 'Dry Goods')
INSERT INTO product_service.product_category_assignments (product_id, category_id)
SELECT flour_product.id, baking_category.id FROM flour_product, baking_category
UNION ALL
SELECT flour_product.id, dry_goods_category.id FROM flour_product, dry_goods_category;

WITH butter_product AS (SELECT id FROM product_service.products WHERE name = 'Butter'),
     dairy_category AS (SELECT id FROM product_service.product_categories WHERE name = 'Dairy Products')
INSERT INTO product_service.product_category_assignments (product_id, category_id)
SELECT butter_product.id, dairy_category.id FROM butter_product, dairy_category;

-- Add migration tracking
CREATE TABLE IF NOT EXISTS public.schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO public.schema_migrations (version) VALUES ('001_initial_product_service');
