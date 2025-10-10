-- PostgreSQL Schema for Research Assistant
-- Usage: psql "postgresql://user:pass@host:5432/dbname" -f database_schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Auto-update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Credit balances table
CREATE TABLE IF NOT EXISTS credit_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) NOT NULL DEFAULT 'default',
    month_year VARCHAR(7) NOT NULL,
    current_balance INTEGER NOT NULL,
    monthly_limit INTEGER NOT NULL DEFAULT 1000,
    total_used_this_month INTEGER NOT NULL DEFAULT 0,
    total_researches_this_month INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1
);

-- Credit transactions table
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    balance_id UUID NOT NULL REFERENCES credit_balances(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    research_request_id VARCHAR(100),
    research_depth VARCHAR(20)
);


-- Indexes
CREATE INDEX IF NOT EXISTS idx_credit_balance_user_month ON credit_balances(user_id, month_year);
CREATE INDEX IF NOT EXISTS idx_credit_balance_updated ON credit_balances(updated_at);
CREATE INDEX IF NOT EXISTS idx_credit_transaction_request ON credit_transactions(research_request_id);
CREATE INDEX IF NOT EXISTS idx_credit_transaction_timestamp ON credit_transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_credit_transaction_balance ON credit_transactions(balance_id);

-- Triggers
CREATE TRIGGER update_credit_balances_updated_at
    BEFORE UPDATE ON credit_balances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


