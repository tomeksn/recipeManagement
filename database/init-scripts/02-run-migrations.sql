-- Database Initialization Script
-- Description: Run all initial migrations in correct order
-- Created: 2025-01-24
-- Author: System

-- Create migration tracking table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Run migrations directly (psql \i command works outside of DO blocks)
\i /docker-entrypoint-initdb.d/../migrations/001_initial_product_service.sql
\i /docker-entrypoint-initdb.d/../migrations/002_initial_recipe_service.sql
\i /docker-entrypoint-initdb.d/../migrations/003_initial_calculator_service.sql

-- Record migrations as applied
INSERT INTO public.schema_migrations (version) VALUES ('001_initial_product_service') ON CONFLICT DO NOTHING;
INSERT INTO public.schema_migrations (version) VALUES ('002_initial_recipe_service') ON CONFLICT DO NOTHING;
INSERT INTO public.schema_migrations (version) VALUES ('003_initial_calculator_service') ON CONFLICT DO NOTHING;

-- Display applied migrations
SELECT version, applied_at FROM public.schema_migrations ORDER BY applied_at;