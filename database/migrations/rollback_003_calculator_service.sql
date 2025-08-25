-- Rollback Migration: 003_initial_calculator_service.sql
-- Description: Rollback script for Calculator Service schema
-- Created: 2025-01-24
-- Author: System

-- Remove migration tracking
DELETE FROM public.schema_migrations WHERE version = '003_initial_calculator_service';

-- Drop all calculator service tables in reverse dependency order
DROP TRIGGER IF EXISTS update_calculation_templates_updated_at ON calculator_service.calculation_templates;

DROP FUNCTION IF EXISTS calculator_service.update_cache_access();
DROP FUNCTION IF EXISTS calculator_service.cleanup_expired_cache();
DROP FUNCTION IF EXISTS calculator_service.evict_lru_cache(INTEGER);
DROP FUNCTION IF EXISTS calculator_service.generate_cache_key(UUID, calculator_service.calculation_type, DECIMAL, VARCHAR, JSONB);
DROP FUNCTION IF EXISTS calculator_service.update_performance_metrics();
DROP FUNCTION IF EXISTS calculator_service.update_updated_at_column();

DROP TABLE IF EXISTS calculator_service.calculation_templates;
DROP TABLE IF EXISTS calculator_service.calculation_performance_metrics;
DROP TABLE IF EXISTS calculator_service.calculation_history;
DROP TABLE IF EXISTS calculator_service.calculation_cache;
DROP TABLE IF EXISTS calculator_service.calculations;

DROP TYPE IF EXISTS calculator_service.cache_priority;
DROP TYPE IF EXISTS calculator_service.calculation_status;
DROP TYPE IF EXISTS calculator_service.calculation_type;

-- Revoke permissions
REVOKE ALL PRIVILEGES ON SCHEMA calculator_service FROM recipe_user;
REVOKE USAGE ON SCHEMA calculator_service FROM recipe_user;

-- Drop schema
DROP SCHEMA IF EXISTS calculator_service CASCADE;
