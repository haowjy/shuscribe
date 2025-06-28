# Supabase Database Setup

This directory contains the Supabase database schema and migration files for ShuScribe.

## Quick Setup

### 1. Supabase Project Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Get your project URL and anon key from the project settings
3. Update your `.env` file with the Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here  # Optional, for admin operations
SKIP_DATABASE=false  # Set to true to use in-memory repositories for testing
```

### 2. Apply Database Migrations

#### Option A: Using Supabase CLI (Recommended)

1. Install the Supabase CLI:
```bash
npm install -g supabase
```

2. Initialize Supabase in your project:
```bash
# From the backend directory
cd backend
supabase init
```

3. Link to your remote project:
```bash
supabase link --project-ref your-project-ref
```

4. Apply migrations:
```bash
supabase db push
```

#### Option B: Manual SQL Execution

1. Copy the contents of `migrations/001_initial_schema.sql`
2. Go to your Supabase dashboard → SQL Editor
3. Paste and execute the migration SQL

### 3. Configure Row Level Security (RLS)

The migration automatically sets up RLS policies, but ensure your authentication is properly configured:

1. Go to Authentication → Settings in your Supabase dashboard
2. Configure your authentication providers (email, OAuth, etc.)
3. Update the JWT secret in your environment if needed

## Database Schema

### Tables

#### `users`
- `id` (UUID, Primary Key)
- `email` (TEXT, Unique)
- `subscription_tier` (TEXT, Default: 'free_byok')
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

#### `user_api_keys`
- `user_id` (UUID, Foreign Key to users.id)
- `provider` (TEXT, e.g., 'openai', 'anthropic')
- `encrypted_api_key` (TEXT)
- `provider_metadata` (JSONB, Optional)
- `validation_status` (TEXT, Default: 'pending')
- `last_validated_at` (TIMESTAMPTZ, Optional)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

**Composite Primary Key:** (user_id, provider)

### Security Features

- **Row Level Security (RLS)** enabled on all tables
- Users can only access their own data
- Automatic `updated_at` timestamp triggers
- Foreign key constraints for data integrity

## Development Mode

To run the application without a database (using in-memory repositories):

```bash
# In your .env file
SKIP_DATABASE=true
```

This is useful for:
- Local development without setting up Supabase
- Testing the LLM service with direct API keys
- CI/CD environments where database setup is not needed

## Environment Variables

```bash
# Required for Supabase connection
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key-here

# Optional for admin operations
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Development mode
SKIP_DATABASE=false  # Set to true to use in-memory repositories

# Legacy (kept for migration compatibility)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/shuscribe
```

## Migration Files

- `001_initial_schema.sql` - Initial database schema with users and API keys tables

## Testing

The repository pattern allows you to easily switch between database modes:

1. **With Supabase:** Set `SKIP_DATABASE=false` and provide valid Supabase credentials
2. **In-Memory:** Set `SKIP_DATABASE=true` for testing without database dependency

## Troubleshooting

### Connection Issues
- Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that your Supabase project is active
- Ensure RLS policies allow your operations

### Migration Issues
- Verify the SQL syntax in your Supabase SQL editor
- Check that the `uuid-ossp` extension is enabled
- Ensure you have the necessary permissions

### Development Mode
- If you want to test without database setup, use `SKIP_DATABASE=true`
- In-memory mode automatically handles all repository operations
- Perfect for LLM service testing with direct API keys 