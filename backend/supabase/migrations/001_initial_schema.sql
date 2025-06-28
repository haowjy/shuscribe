-- backend/supabase/migrations/001_initial_schema.sql
-- Initial schema for ShuScribe database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    subscription_tier TEXT NOT NULL DEFAULT 'free_byok',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create user_api_keys table
CREATE TABLE IF NOT EXISTS user_api_keys (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    encrypted_api_key TEXT NOT NULL,
    provider_metadata JSONB,
    validation_status TEXT NOT NULL DEFAULT 'pending',
    last_validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    
    -- Composite primary key (user_id + provider)
    PRIMARY KEY (user_id, provider)
);

-- Create index for faster lookups by user_id
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON user_api_keys(user_id);

-- Create index for faster lookups by provider
CREATE INDEX IF NOT EXISTS idx_user_api_keys_provider ON user_api_keys(provider);

-- Add a trigger to automatically update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to both tables
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_api_keys_updated_at 
    BEFORE UPDATE ON user_api_keys 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row Level Security) policies for users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Allow users to read their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- Allow users to update their own data
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Create RLS policies for user_api_keys table
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;

-- Allow users to manage their own API keys
CREATE POLICY "Users can manage own API keys" ON user_api_keys
    FOR ALL USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON TABLE users TO anon, authenticated;
GRANT ALL ON TABLE user_api_keys TO anon, authenticated; 