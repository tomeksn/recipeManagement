-- Rollback Migration: 001_initial_product_service.sql
-- Description: Rollback script for Product Service schema
-- Created: 2025-01-24
-- Author: System

-- Remove migration tracking
DELETE FROM public.schema_migrations WHERE version = '001_initial_product_service';

-- Drop all product service tables in reverse dependency order
DROP TRIGGER IF EXISTS products_audit_trigger ON product_service.products;
DROP TRIGGER IF EXISTS update_products_updated_at ON product_service.products;

DROP FUNCTION IF EXISTS product_service.log_product_changes();
DROP FUNCTION IF EXISTS product_service.update_updated_at_column();
DROP FUNCTION IF EXISTS product_service.search_products_fuzzy(TEXT, INTEGER, REAL);
DROP FUNCTION IF EXISTS product_service.cleanup_expired_search_cache();

DROP TABLE IF EXISTS product_service.product_search_cache;
DROP TABLE IF EXISTS product_service.product_tag_assignments;
DROP TABLE IF EXISTS product_service.product_tags;
DROP TABLE IF EXISTS product_service.product_category_assignments;
DROP TABLE IF EXISTS product_service.product_categories;
DROP TABLE IF EXISTS product_service.products_audit;
DROP TABLE IF EXISTS product_service.products;

DROP TYPE IF EXISTS product_service.product_unit;
DROP TYPE IF EXISTS product_service.product_type;

-- Revoke permissions
REVOKE ALL PRIVILEGES ON SCHEMA product_service FROM recipe_user;
REVOKE USAGE ON SCHEMA product_service FROM recipe_user;

-- Drop schema
DROP SCHEMA IF EXISTS product_service CASCADE;

-- Note: Extensions are not dropped as they might be used by other services
-- DROP EXTENSION IF EXISTS btree_gin;
-- DROP EXTENSION IF EXISTS pg_trgm;
-- DROP EXTENSION IF EXISTS "uuid-ossp";
