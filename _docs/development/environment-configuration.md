# Environment Configuration Guide

This document provides comprehensive guidance on ShuScribe backend environment configuration and behaviors. All environment variables should be verified against this documentation when making changes.

## Overview

The ShuScribe backend uses environment-specific configuration to control application behavior, database settings, security, and debugging features. The configuration is primarily driven by the `ENVIRONMENT` variable with additional fine-tuning through other settings.

## Environment Variables

### Core Environment Settings

#### `ENVIRONMENT`
**Values**: `development` | `testing` | `production`  
**Default**: `development`

Controls the primary application behavior mode:

- **`development`**: Maximum flexibility for local development
  - Pydantic validation: Extra fields ignored (flexible schema validation)
  - Database seeding: Allowed
  - Default table prefix: `test_` (if TABLE_PREFIX not set)
  - API documentation: Available when DEBUG=true
  - SQL query logging: Enabled when DEBUG=true

- **`testing`**: Strict validation for test environments
  - Pydantic validation: Extra fields forbidden (strict schema validation)
  - Database seeding: Allowed (for test data setup)
  - Default table prefix: `test_` (if TABLE_PREFIX not set)
  - API documentation: Only available when DEBUG=true
  - SQL query logging: Only when DEBUG=true

- **`production`**: Maximum security and performance
  - Pydantic validation: Extra fields forbidden (strict schema validation)
  - Database seeding: **Completely blocked** for security
  - Table prefix: None (empty string)
  - API documentation: Only available when DEBUG=true (not recommended)
  - SQL query logging: Only when DEBUG=true (not recommended)

#### `DEBUG`
**Values**: `true` | `false`  
**Default**: `true`

Controls debugging features across all environments:

- **`true`**: Enables debugging features
  - FastAPI documentation endpoints (`/docs`, `/redoc`) available
  - SQL query logging to console (echo=True)
  - Additional debug logging in application
  - Enhanced error messages

- **`false`**: Disables debugging features
  - No API documentation endpoints
  - No SQL query logging
  - Minimal debug output
  - Production-ready logging

### Database Configuration

#### `DATABASE_BACKEND`
**Values**: `memory` | `file` | `database`  
**Default**: `database`

Controls the database storage backend:

- **`memory`**: In-memory SQLite database
  - Use case: Testing, development with throwaway data
  - Data persistence: None (lost on restart)
  - Performance: Fastest
  - Isolation: Complete isolation between runs

- **`file`**: File-based SQLite database
  - Use case: Local development with persistent data
  - Data persistence: Persists between restarts
  - Performance: Good for development
  - Isolation: Per-file isolation

- **`database`**: PostgreSQL/Supabase database
  - Use case: Production, shared development environments
  - Data persistence: Full persistence with backups
  - Performance: Production-ready
  - Isolation: Controlled by TABLE_PREFIX

#### `TABLE_PREFIX`
**Values**: Any string (common: `dev_`, `test_`, `staging_`)  
**Default**: Environment-dependent

Controls database table naming for environment isolation:

- **Development/Testing**: Defaults to `test_` if not specified
- **Production**: Defaults to empty string (no prefix)
- **Custom**: Use custom prefixes for multiple dev environments

**Examples**:
```bash
# Developer-specific isolation
TABLE_PREFIX=jimmy_dev_

# Feature branch isolation  
TABLE_PREFIX=feature_auth_

# Staging environment
TABLE_PREFIX=staging_
```

### Database Connection Settings

#### Connection Timeouts
```bash
DATABASE_COMMAND_TIMEOUT=60    # Query execution timeout (seconds)
DATABASE_POOL_TIMEOUT=30       # Connection acquisition timeout (seconds)
DATABASE_CONNECT_TIMEOUT=30    # Initial connection timeout (seconds)
```

#### Connection Pool Settings
```bash
DATABASE_POOL_SIZE=20          # Base connections maintained in pool
DATABASE_MAX_OVERFLOW=30       # Additional connections beyond pool_size
                              # Total max connections = POOL_SIZE + MAX_OVERFLOW
```

### Database Seeding Configuration

#### `ENABLE_DATABASE_SEEDING`
**Values**: `true` | `false`  
**Default**: `false`  
**Environment Restriction**: Only works in `development` and `testing`

Controls automatic database seeding behavior:

- **`false`**: No automatic seeding
- **`true`**: Seeds database if empty on startup (development/testing only)

#### `SEED_DATA_SIZE`
**Values**: `small` | `medium` | `large`  
**Default**: `medium`

Controls the amount of test data generated:

- **`small`**: Minimal test data for basic functionality
- **`medium`**: Moderate amount of test data for full feature testing
- **`large`**: Extensive test data for performance and stress testing

#### `CLEAR_BEFORE_SEED`
**Values**: `true` | `false`  
**Default**: `false`

Controls whether to clear existing data before seeding:

- **`false`**: Only seed if database is empty
- **`true`**: Clear all data before seeding (destructive)

## Environment-Specific Behaviors

### Security and Validation

| Feature | Development | Testing | Production |
|---------|-------------|---------|------------|
| Pydantic Extra Fields | Ignored | Forbidden | Forbidden |
| Database Seeding | Allowed | Allowed | **Blocked** |
| Default Table Prefix | `test_` | `test_` | None |
| API Documentation | If DEBUG=true | If DEBUG=true | If DEBUG=true |
| SQL Query Logging | If DEBUG=true | If DEBUG=true | If DEBUG=true |

### Configuration Validation

The backend performs different levels of configuration validation based on environment:

- **Development**: Lenient validation, allows extra configuration
- **Testing/Production**: Strict validation, rejects unknown configuration

### Logging Behavior

- **Console Logging**: Always DEBUG level during startup
- **Application Logging**: Controlled by LOG_LEVEL environment variable
- **SQL Logging**: Controlled by DEBUG flag and database engine echo setting

## Common Environment Setups

### Local Development
```bash
ENVIRONMENT=development
DEBUG=true
DATABASE_BACKEND=database  # or 'file' for SQLite
TABLE_PREFIX=dev_
ENABLE_DATABASE_SEEDING=true
SEED_DATA_SIZE=medium
```

### Testing Environment
```bash
ENVIRONMENT=testing
DEBUG=false
DATABASE_BACKEND=memory  # or 'database' for persistent tests
TABLE_PREFIX=test_
ENABLE_DATABASE_SEEDING=true
SEED_DATA_SIZE=small
CLEAR_BEFORE_SEED=true
```

### Staging Environment
```bash
ENVIRONMENT=testing  # Use testing for staging-like behavior
DEBUG=false
DATABASE_BACKEND=database
TABLE_PREFIX=staging_
ENABLE_DATABASE_SEEDING=false
```

### Production Environment
```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_BACKEND=database
TABLE_PREFIX=  # Empty for production
ENABLE_DATABASE_SEEDING=false
```

## Environment Migration Guidelines

### Development → Testing
1. Change `ENVIRONMENT=testing`
2. Set `DEBUG=false`
3. Ensure `TABLE_PREFIX` provides isolation
4. Consider using `memory` backend for faster tests

### Testing → Production
1. Change `ENVIRONMENT=production`
2. Ensure `DEBUG=false`
3. Remove or empty `TABLE_PREFIX`
4. Set `ENABLE_DATABASE_SEEDING=false`
5. Review all security settings

## Troubleshooting

### Common Issues

#### "Database seeding is only allowed in development/testing environments"
- **Cause**: Trying to seed in production environment
- **Solution**: Change `ENVIRONMENT` to `development` or `testing`

#### "Extra fields forbidden"
- **Cause**: Unknown configuration in testing/production environment
- **Solution**: Remove unknown config or switch to development environment

#### Connection timeouts
- **Cause**: Database connection issues, especially on WSL2 or slow networks
- **Solution**: Increase timeout values in database configuration

#### Table not found errors
- **Cause**: Mismatched `TABLE_PREFIX` between environments
- **Solution**: Ensure consistent table prefix or run database migrations

### Debug Mode Verification

To verify your environment configuration:

1. **Check startup logs**: Look for environment and debug status messages
2. **API documentation**: Visit `/docs` - should only work if DEBUG=true
3. **SQL logging**: Check console for SQL queries when DEBUG=true
4. **Table names**: Verify tables have expected prefixes in database

## Security Considerations

### Production Security Checklist

- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `ENABLE_DATABASE_SEEDING=false`
- [ ] `TABLE_PREFIX=""` (empty)
- [ ] Strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Restricted `ALLOWED_ORIGINS`
- [ ] Secure database connection (TLS)

### Development Security Notes

- Never commit real API keys to git
- Use strong encryption keys even in development
- Be cautious with `CLEAR_BEFORE_SEED=true` (destructive)
- Regularly rotate development credentials

## Related Documentation

- **Main Guide**: [CLAUDE.md](../../CLAUDE.md) - Project overview and integration
- **Backend Guide**: [backend/CLAUDE-backend.md](../../backend/CLAUDE-backend.md) - Backend-specific development
- **API Reference**: [API Reference](../core/api-reference.md) - Complete API documentation
- **Deployment Guide**: [deployment-guide.md](deployment-guide.md) - Production deployment process

---

**⚠️ Important**: Always verify environment behavior against this documentation when making configuration changes. Update this document when adding new environment-dependent features.