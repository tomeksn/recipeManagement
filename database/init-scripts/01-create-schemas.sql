-- Create schemas for each microservice
CREATE SCHEMA IF NOT EXISTS product_service;
CREATE SCHEMA IF NOT EXISTS recipe_service;
CREATE SCHEMA IF NOT EXISTS calculator_service;

-- Grant permissions to the recipe_user
GRANT ALL PRIVILEGES ON SCHEMA product_service TO recipe_user;
GRANT ALL PRIVILEGES ON SCHEMA recipe_service TO recipe_user;
GRANT ALL PRIVILEGES ON SCHEMA calculator_service TO recipe_user;

-- Set default search path for each service
-- This will be overridden by each service's configuration
ALTER USER recipe_user SET search_path = public, product_service, recipe_service, calculator_service;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure the user can create tables in all schemas
GRANT CREATE ON SCHEMA product_service TO recipe_user;
GRANT CREATE ON SCHEMA recipe_service TO recipe_user;
GRANT CREATE ON SCHEMA calculator_service TO recipe_user;
