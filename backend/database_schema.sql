-- PostgreSQL Schema for Research Assistant
-- Run this script manually on your database before starting the application
-- 
-- Usage:
--   psql -h <host> -U <user> -d <database> -f database_schema.sql
-- Or using your database URL:
--   psql "postgresql://user:pass@host:5432/dbname" -f database_schema.sql

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- Table: credit_balances
-- Description: Tracks user credit balances per month with ACID compliance
-- =============================================================================
CREATE TABLE IF NOT EXISTS credit_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) NOT NULL DEFAULT 'default',
    month_year VARCHAR(7) NOT NULL,  -- Format: "2024-10"
    
    -- Balance tracking
    current_balance INTEGER NOT NULL,
    monthly_limit INTEGER NOT NULL DEFAULT 1000,
    
    -- Usage statistics
    total_used_this_month INTEGER NOT NULL DEFAULT 0,
    total_researches_this_month INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Version for optimistic locking
    version INTEGER NOT NULL DEFAULT 1
);

-- Indexes for credit_balances
CREATE INDEX IF NOT EXISTS idx_credit_balance_user_month 
    ON credit_balances(user_id, month_year);

CREATE INDEX IF NOT EXISTS idx_credit_balance_updated 
    ON credit_balances(updated_at);

-- =============================================================================
-- Table: credit_transactions
-- Description: Individual credit transactions with detailed API usage tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    
    -- Foreign key to credit_balances
    balance_id UUID NOT NULL REFERENCES credit_balances(id) ON DELETE CASCADE,
    
    -- Transaction details
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Research context
    research_request_id VARCHAR(100),
    research_depth VARCHAR(20)
);

-- Indexes for credit_transactions
CREATE INDEX IF NOT EXISTS idx_credit_transaction_request 
    ON credit_transactions(research_request_id);

CREATE INDEX IF NOT EXISTS idx_credit_transaction_timestamp 
    ON credit_transactions(timestamp);

CREATE INDEX IF NOT EXISTS idx_credit_transaction_balance 
    ON credit_transactions(balance_id);

-- =============================================================================
-- Trigger: Auto-update updated_at timestamp on credit_balances
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_credit_balances_updated_at
    BEFORE UPDATE ON credit_balances
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Verification Query
-- Description: Run this to verify all tables were created successfully
-- =============================================================================
-- SELECT 
--     table_name,
--     (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
-- FROM information_schema.tables t
-- WHERE table_schema = 'public' 
--     AND table_name IN ('credit_balances', 'credit_transactions')
-- ORDER BY table_name;

-- =============================================================================
-- Sample Data (Optional - for testing)
-- =============================================================================
-- Uncomment to insert sample data for testing:

-- INSERT INTO credit_balances (user_id, month_year, current_balance, monthly_limit)
-- VALUES ('default', '2024-10', 1000, 1000)
-- ON CONFLICT DO NOTHING;

