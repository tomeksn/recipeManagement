-- Calculator Service Database Schema
-- This file defines the complete database schema for the Calculator Service

-- Create the calculator_service schema
CREATE SCHEMA IF NOT EXISTS calculator_service;

-- Set search path for this session
SET search_path TO calculator_service, public;

-- Create ENUM types for calculation management
CREATE TYPE calculation_type AS ENUM ('scale_by_quantity', 'scale_by_weight', 'unit_conversion', 'nutritional');
CREATE TYPE calculation_status AS ENUM ('pending', 'completed', 'failed', 'cached');
CREATE TYPE cache_priority AS ENUM ('low', 'medium', 'high', 'critical');

-- Create calculations table for storing calculation requests and results
CREATE TABLE calculations (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Calculation request information
    recipe_id UUID NOT NULL, -- References recipe_service.recipes(id)
    product_id UUID NOT NULL, -- References product_service.products(id)
    calculation_type calculation_type NOT NULL,
    
    -- Input parameters
    target_quantity DECIMAL(12,4) NOT NULL,
    target_unit VARCHAR(20) NOT NULL,
    input_parameters JSONB NOT NULL, -- Flexible parameters for different calculation types
    
    -- Calculation results
    result_data JSONB, -- Calculated ingredient quantities and details
    total_weight DECIMAL(12,4), -- Total calculated weight
    total_pieces INTEGER, -- Total calculated pieces (if applicable)
    calculation_summary TEXT, -- Human-readable summary
    
    -- Performance and metadata
    calculation_time_ms INTEGER, -- Time taken to perform calculation
    cache_key VARCHAR(255) UNIQUE, -- Unique key for caching
    status calculation_status NOT NULL DEFAULT 'pending',
    error_message TEXT, -- Error details if calculation failed
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    requested_by UUID, -- User who requested calculation
    
    -- Business constraints
    CONSTRAINT calculations_target_quantity_positive CHECK (target_quantity > 0),
    CONSTRAINT calculations_total_weight_non_negative CHECK (total_weight IS NULL OR total_weight >= 0),
    CONSTRAINT calculations_total_pieces_non_negative CHECK (total_pieces IS NULL OR total_pieces >= 0),
    CONSTRAINT calculations_calculation_time_non_negative CHECK (calculation_time_ms IS NULL OR calculation_time_ms >= 0)
);

-- Create indexes for calculations
CREATE INDEX idx_calculations_recipe_id ON calculations(recipe_id);
CREATE INDEX idx_calculations_product_id ON calculations(product_id);
CREATE INDEX idx_calculations_type ON calculations(calculation_type);
CREATE INDEX idx_calculations_status ON calculations(status);
CREATE INDEX idx_calculations_cache_key ON calculations(cache_key);
CREATE INDEX idx_calculations_created_at ON calculations(created_at);
CREATE INDEX idx_calculations_completed_at ON calculations(completed_at);

-- Create calculation_cache table for high-performance caching
CREATE TABLE calculation_cache (
    -- Cache key components
    cache_key VARCHAR(255) PRIMARY KEY,
    cache_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of input parameters
    
    -- Cached data
    recipe_id UUID NOT NULL,
    product_id UUID NOT NULL,
    calculation_type calculation_type NOT NULL,
    input_parameters JSONB NOT NULL,
    result_data JSONB NOT NULL,
    
    -- Cache metadata
    cache_priority cache_priority NOT NULL DEFAULT 'medium',
    access_count INTEGER NOT NULL DEFAULT 1,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Performance tracking
    calculation_time_ms INTEGER,
    cache_size_bytes INTEGER, -- Approximate size of cached data
    
    -- Constraints
    CONSTRAINT calculation_cache_access_count_positive CHECK (access_count > 0),
    CONSTRAINT calculation_cache_cache_size_positive CHECK (cache_size_bytes IS NULL OR cache_size_bytes > 0)
);

-- Create indexes for calculation cache
CREATE INDEX idx_calculation_cache_recipe_id ON calculation_cache(recipe_id);
CREATE INDEX idx_calculation_cache_product_id ON calculation_cache(product_id);
CREATE INDEX idx_calculation_cache_type ON calculation_cache(calculation_type);
CREATE INDEX idx_calculation_cache_hash ON calculation_cache(cache_hash);
CREATE INDEX idx_calculation_cache_expires_at ON calculation_cache(expires_at);
CREATE INDEX idx_calculation_cache_last_accessed ON calculation_cache(last_accessed);
CREATE INDEX idx_calculation_cache_priority ON calculation_cache(cache_priority);
CREATE INDEX idx_calculation_cache_access_count ON calculation_cache(access_count);

-- Create calculation_history table for tracking usage patterns
CREATE TABLE calculation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Calculation reference
    calculation_id UUID REFERENCES calculations(id) ON DELETE SET NULL,
    cache_key VARCHAR(255),
    
    -- Request details
    recipe_id UUID NOT NULL,
    product_id UUID NOT NULL,
    calculation_type calculation_type NOT NULL,
    target_quantity DECIMAL(12,4) NOT NULL,
    target_unit VARCHAR(20) NOT NULL,
    
    -- Response details
    was_cached BOOLEAN NOT NULL DEFAULT FALSE,
    calculation_time_ms INTEGER,
    result_size_bytes INTEGER,
    
    -- User and session tracking
    requested_by UUID,
    session_id VARCHAR(255),
    user_agent TEXT,
    ip_address INET,
    
    -- Timing
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraints
    CONSTRAINT calculation_history_target_quantity_positive CHECK (target_quantity > 0),
    CONSTRAINT calculation_history_calculation_time_non_negative CHECK (calculation_time_ms IS NULL OR calculation_time_ms >= 0),
    CONSTRAINT calculation_history_result_size_non_negative CHECK (result_size_bytes IS NULL OR result_size_bytes >= 0)
);

-- Create indexes for calculation history
CREATE INDEX idx_calculation_history_calculation_id ON calculation_history(calculation_id);
CREATE INDEX idx_calculation_history_recipe_id ON calculation_history(recipe_id);
CREATE INDEX idx_calculation_history_product_id ON calculation_history(product_id);
CREATE INDEX idx_calculation_history_requested_at ON calculation_history(requested_at);
CREATE INDEX idx_calculation_history_requested_by ON calculation_history(requested_by);
CREATE INDEX idx_calculation_history_was_cached ON calculation_history(was_cached);

-- Create calculation_performance_metrics table for monitoring
CREATE TABLE calculation_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Time period for metrics
    metric_date DATE NOT NULL,
    metric_hour INTEGER CHECK (metric_hour >= 0 AND metric_hour <= 23),
    
    -- Calculation statistics
    total_calculations INTEGER NOT NULL DEFAULT 0,
    cached_calculations INTEGER NOT NULL DEFAULT 0,
    failed_calculations INTEGER NOT NULL DEFAULT 0,
    
    -- Performance metrics
    avg_calculation_time_ms DECIMAL(10,2),
    min_calculation_time_ms INTEGER,
    max_calculation_time_ms INTEGER,
    p95_calculation_time_ms INTEGER, -- 95th percentile
    
    -- Cache statistics
    cache_hit_rate DECIMAL(5,4), -- Percentage as decimal (0.0-1.0)
    cache_evictions INTEGER NOT NULL DEFAULT 0,
    
    -- Resource usage
    total_memory_used_mb DECIMAL(10,2),
    peak_memory_used_mb DECIMAL(10,2),
    
    -- Update tracking
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Unique constraint for time periods
    UNIQUE (metric_date, metric_hour)
);

-- Create indexes for performance metrics
CREATE INDEX idx_calculation_performance_metrics_date ON calculation_performance_metrics(metric_date);
CREATE INDEX idx_calculation_performance_metrics_hour ON calculation_performance_metrics(metric_hour);
CREATE INDEX idx_calculation_performance_metrics_updated_at ON calculation_performance_metrics(updated_at);

-- Create calculation_templates table for common calculation patterns
CREATE TABLE calculation_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Template information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    calculation_type calculation_type NOT NULL,
    
    -- Template parameters
    template_parameters JSONB NOT NULL,
    default_values JSONB,
    validation_rules JSONB,
    
    -- Usage tracking
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT calculation_templates_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT calculation_templates_usage_count_non_negative CHECK (usage_count >= 0)
);

-- Create indexes for calculation templates
CREATE INDEX idx_calculation_templates_name ON calculation_templates(name);
CREATE INDEX idx_calculation_templates_type ON calculation_templates(calculation_type);
CREATE INDEX idx_calculation_templates_usage_count ON calculation_templates(usage_count);
CREATE INDEX idx_calculation_templates_is_active ON calculation_templates(is_active);

-- Create function to update cache access statistics
CREATE OR REPLACE FUNCTION update_cache_access()
RETURNS TRIGGER AS $$
BEGIN
    NEW.access_count = OLD.access_count + 1;
    NEW.last_accessed = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM calculation_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to evict least recently used cache entries
CREATE OR REPLACE FUNCTION evict_lru_cache(max_entries INTEGER DEFAULT 10000)
RETURNS INTEGER AS $$
DECLARE
    current_count INTEGER;
    deleted_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO current_count FROM calculation_cache;
    
    IF current_count > max_entries THEN
        WITH lru_entries AS (
            SELECT cache_key
            FROM calculation_cache
            ORDER BY 
                cache_priority DESC, -- Keep high priority items
                last_accessed ASC, -- Evict least recently used
                access_count ASC -- Evict least accessed
            OFFSET max_entries
        )
        DELETE FROM calculation_cache
        WHERE cache_key IN (SELECT cache_key FROM lru_entries);
        
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RETURN deleted_count;
    END IF;
    
    RETURN 0;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate cache key
CREATE OR REPLACE FUNCTION generate_cache_key(
    p_recipe_id UUID,
    p_calculation_type calculation_type,
    p_target_quantity DECIMAL,
    p_target_unit VARCHAR,
    p_parameters JSONB
)
RETURNS VARCHAR(255) AS $$
DECLARE
    param_hash VARCHAR(64);
BEGIN
    -- Create hash of parameters for consistent cache key
    param_hash := encode(
        digest(
            concat(
                p_recipe_id::TEXT,
                p_calculation_type::TEXT,
                p_target_quantity::TEXT,
                p_target_unit,
                p_parameters::TEXT
            ),
            'sha256'
        ),
        'hex'
    );
    
    RETURN concat('calc_', left(param_hash, 32));
END;
$$ LANGUAGE plpgsql;

-- Create function to update performance metrics
CREATE OR REPLACE FUNCTION update_performance_metrics()
RETURNS VOID AS $$
DECLARE
    current_date DATE := CURRENT_DATE;
    current_hour INTEGER := EXTRACT(HOUR FROM CURRENT_TIMESTAMP);
BEGIN
    INSERT INTO calculation_performance_metrics (
        metric_date,
        metric_hour,
        total_calculations,
        cached_calculations,
        failed_calculations,
        avg_calculation_time_ms,
        min_calculation_time_ms,
        max_calculation_time_ms,
        cache_hit_rate
    )
    SELECT 
        current_date,
        current_hour,
        COUNT(*) as total_calculations,
        COUNT(*) FILTER (WHERE was_cached = true) as cached_calculations,
        0 as failed_calculations, -- Will be updated separately
        AVG(calculation_time_ms) as avg_calculation_time_ms,
        MIN(calculation_time_ms) as min_calculation_time_ms,
        MAX(calculation_time_ms) as max_calculation_time_ms,
        COALESCE(
            COUNT(*) FILTER (WHERE was_cached = true)::DECIMAL / NULLIF(COUNT(*), 0),
            0
        ) as cache_hit_rate
    FROM calculation_history
    WHERE requested_at >= date_trunc('hour', CURRENT_TIMESTAMP)
    AND requested_at < date_trunc('hour', CURRENT_TIMESTAMP) + INTERVAL '1 hour'
    ON CONFLICT (metric_date, metric_hour) DO UPDATE SET
        total_calculations = EXCLUDED.total_calculations,
        cached_calculations = EXCLUDED.cached_calculations,
        avg_calculation_time_ms = EXCLUDED.avg_calculation_time_ms,
        min_calculation_time_ms = EXCLUDED.min_calculation_time_ms,
        max_calculation_time_ms = EXCLUDED.max_calculation_time_ms,
        cache_hit_rate = EXCLUDED.cache_hit_rate,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Create function for updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_calculation_templates_updated_at 
    BEFORE UPDATE ON calculation_templates 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT USAGE ON SCHEMA calculator_service TO recipe_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA calculator_service TO recipe_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA calculator_service TO recipe_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA calculator_service TO recipe_user;

-- Add comments for documentation
COMMENT ON SCHEMA calculator_service IS 'Schema for the Calculator Service microservice';
COMMENT ON TABLE calculations IS 'Main table for calculation requests and results';
COMMENT ON TABLE calculation_cache IS 'High-performance cache for frequently requested calculations';
COMMENT ON TABLE calculation_history IS 'Historical log of all calculation requests';
COMMENT ON TABLE calculation_performance_metrics IS 'Performance monitoring and metrics';
COMMENT ON TABLE calculation_templates IS 'Reusable calculation templates and patterns';

COMMENT ON COLUMN calculations.recipe_id IS 'References the recipe being calculated';
COMMENT ON COLUMN calculations.target_quantity IS 'Target quantity for scaling calculation';
COMMENT ON COLUMN calculations.input_parameters IS 'Flexible JSON parameters for calculation';
COMMENT ON COLUMN calculations.result_data IS 'Calculated results in JSON format';
COMMENT ON COLUMN calculations.cache_key IS 'Unique cache key for result caching';

COMMENT ON COLUMN calculation_cache.cache_priority IS 'Priority level for cache eviction';
COMMENT ON COLUMN calculation_cache.access_count IS 'Number of times this cache entry was accessed';
COMMENT ON COLUMN calculation_cache.expires_at IS 'Expiration timestamp for cache entry';

-- Reset search path
RESET search_path;
