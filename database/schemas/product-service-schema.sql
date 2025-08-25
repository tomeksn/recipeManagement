-- Product Service Database Schema
-- This file defines the complete database schema for the Product Service

-- Create the product_service schema
CREATE SCHEMA IF NOT EXISTS product_service;

-- Set search path for this session
SET search_path TO product_service, public;

-- Create ENUM types for product categorization
CREATE TYPE product_type AS ENUM ('standard', 'kit', 'semi-product');
CREATE TYPE product_unit AS ENUM ('piece', 'gram');

-- Create products table
CREATE TABLE products (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic product information
    name VARCHAR(255) NOT NULL,
    type product_type NOT NULL DEFAULT 'standard',
    unit product_unit NOT NULL DEFAULT 'piece',
    description TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID, -- Reference to user who created the product
    updated_by UUID, -- Reference to user who last updated the product
    
    -- Business constraints
    CONSTRAINT products_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT products_name_unique UNIQUE (name)
);

-- Create indexes for search optimization
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_type ON products(type);
CREATE INDEX idx_products_unit ON products(unit);
CREATE INDEX idx_products_created_at ON products(created_at);
CREATE INDEX idx_products_updated_at ON products(updated_at);

-- Create full-text search index for product names
CREATE INDEX idx_products_name_fulltext ON products USING gin(to_tsvector('english', name));
CREATE INDEX idx_products_name_trigram ON products USING gin(name gin_trgm_ops);

-- Create products_audit table for tracking changes
CREATE TABLE products_audit (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraints
    CONSTRAINT products_audit_operation_check CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))
);

-- Create index on audit table
CREATE INDEX idx_products_audit_product_id ON products_audit(product_id);
CREATE INDEX idx_products_audit_changed_at ON products_audit(changed_at);

-- Create product_categories table for flexible categorization
CREATE TABLE product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7), -- Hex color code for UI
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT product_categories_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT product_categories_color_format CHECK (color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Create product_category_assignments table for many-to-many relationship
CREATE TABLE product_category_assignments (
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES product_categories(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    PRIMARY KEY (product_id, category_id)
);

-- Create indexes for category assignments
CREATE INDEX idx_product_category_assignments_product_id ON product_category_assignments(product_id);
CREATE INDEX idx_product_category_assignments_category_id ON product_category_assignments(category_id);

-- Create product_tags table for flexible tagging
CREATE TABLE product_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT product_tags_name_not_empty CHECK (length(trim(name)) > 0)
);

-- Create product_tag_assignments table
CREATE TABLE product_tag_assignments (
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES product_tags(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    PRIMARY KEY (product_id, tag_id)
);

-- Create product_search_cache table for search optimization
CREATE TABLE product_search_cache (
    search_term VARCHAR(255) NOT NULL,
    search_hash VARCHAR(64) NOT NULL,
    results JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    PRIMARY KEY (search_hash)
);

-- Create index for search cache cleanup
CREATE INDEX idx_product_search_cache_expires_at ON product_search_cache(expires_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function for audit logging
CREATE OR REPLACE FUNCTION log_product_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO products_audit (product_id, operation, old_values, changed_at)
        VALUES (OLD.id, 'DELETE', to_jsonb(OLD), CURRENT_TIMESTAMP);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO products_audit (product_id, operation, old_values, new_values, changed_at)
        VALUES (NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO products_audit (product_id, operation, new_values, changed_at)
        VALUES (NEW.id, 'INSERT', to_jsonb(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit triggers
CREATE TRIGGER products_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION log_product_changes();

-- Create indexes for performance optimization
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_composite_search 
    ON products(type, unit, name);

-- Create function for fuzzy search
CREATE OR REPLACE FUNCTION search_products_fuzzy(
    search_term TEXT,
    limit_count INTEGER DEFAULT 10,
    similarity_threshold REAL DEFAULT 0.3
)
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    type product_type,
    unit product_unit,
    description TEXT,
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.type,
        p.unit,
        p.description,
        GREATEST(
            similarity(p.name, search_term),
            ts_rank(to_tsvector('english', p.name), plainto_tsquery('english', search_term))
        ) as similarity_score
    FROM products p
    WHERE 
        p.name ILIKE '%' || search_term || '%'
        OR similarity(p.name, search_term) > similarity_threshold
        OR to_tsvector('english', p.name) @@ plainto_tsquery('english', search_term)
    ORDER BY similarity_score DESC, p.name ASC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean up expired search cache
CREATE OR REPLACE FUNCTION cleanup_expired_search_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM product_search_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your user setup)
GRANT USAGE ON SCHEMA product_service TO recipe_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA product_service TO recipe_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA product_service TO recipe_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA product_service TO recipe_user;

-- Enable required extensions for search functionality
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Add comments for documentation
COMMENT ON SCHEMA product_service IS 'Schema for the Product Service microservice';
COMMENT ON TABLE products IS 'Main products table storing all product information';
COMMENT ON TABLE products_audit IS 'Audit trail for all changes to products';
COMMENT ON TABLE product_categories IS 'Product categories for flexible organization';
COMMENT ON TABLE product_tags IS 'Flexible tagging system for products';
COMMENT ON TABLE product_search_cache IS 'Cache table for search optimization';

COMMENT ON COLUMN products.id IS 'Unique identifier for the product';
COMMENT ON COLUMN products.name IS 'Product name - must be unique and non-empty';
COMMENT ON COLUMN products.type IS 'Product type: standard, kit, or semi-product';
COMMENT ON COLUMN products.unit IS 'Unit of measurement: piece or gram';
COMMENT ON COLUMN products.description IS 'Optional detailed description of the product';

-- Reset search path
RESET search_path;
