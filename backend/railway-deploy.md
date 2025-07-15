# Railway Deployment Guide - Two Service Architecture

ShuScribe uses a **two-service architecture** on Railway for optimal performance and separation of concerns:

1. **FastAPI Backend Service** - Your main application
2. **Portkey Gateway Service** - LLM request routing and API key management

## Architecture Benefits

- **Independent Scaling**: Scale backend and LLM gateway based on different usage patterns
- **Deployment Independence**: Update services without affecting each other
- **Resource Optimization**: Different CPU/memory requirements handled separately
- **Security Isolation**: LLM API keys managed in dedicated service
- **Better Monitoring**: Separate logs and metrics for each service

## Quick Deploy Steps

### 1. Connect to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create a new Railway project
railway init

# You'll deploy two services in this project:
# 1. FastAPI Backend (from backend/ directory)
# 2. Portkey Gateway (Docker deployment)
```

### 2. Deploy Service 1: FastAPI Backend

```bash
# Navigate to backend directory
cd backend

# Deploy FastAPI service
railway up

# Name it something like "shuscribe-backend"
```

### 3. Deploy Service 2: Portkey Gateway

```bash
# From Railway dashboard or CLI, add a new service
railway service create

# Deploy using Docker image
# In Railway dashboard:
# - Source: Docker Image
# - Image: portkeyai/gateway:latest
# - Port: 8787
# - Name: "shuscribe-portkey"
```

### 4. Database Setup Options

#### Option A: Use Supabase (Recommended)
- Keep using your existing Supabase database
- Set `DATABASE_URL` to your Supabase connection string
- No additional setup needed

#### Option B: Railway PostgreSQL
```bash
# Add PostgreSQL service to your Railway project
railway add postgresql

# Railway will automatically set DATABASE_URL variable
# Format: postgresql://postgres:password@host:port/database
```

### 5. Configure Environment Variables

#### FastAPI Backend Service Variables
Set these for your **shuscribe-backend** service:

```bash
# Switch to backend service
railway service select shuscribe-backend

# Required variables
railway variables set DEBUG=false
railway variables set ENVIRONMENT=production  
railway variables set SECRET_KEY=your-production-secret-key
railway variables set DATABASE_URL=your-database-connection-string
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_PUBLISHABLE_KEY=your-publishable-key
railway variables set SUPABASE_SECRET_KEY=your-secret-key
railway variables set ENCRYPTION_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set ALLOWED_ORIGINS='["https://your-app.vercel.app"]'

# Connect to Portkey service (get URL from Railway dashboard)
railway variables set PORTKEY_BASE_URL=https://shuscribe-portkey.railway.app/v1
```

#### Portkey Gateway Service Variables
Set these for your **shuscribe-portkey** service:

```bash
# Switch to Portkey service
railway service select shuscribe-portkey

# Basic Portkey configuration
railway variables set NODE_ENV=production
railway variables set PORT=8787

# Optional: Add authentication if needed
# railway variables set PORTKEY_API_KEY=your-portkey-auth-key
```

### 6. Deploy and Connect Services

```bash
# Both services should auto-deploy after configuration
# Check deployment status
railway status

# Test connectivity between services
# Backend should be able to reach Portkey at internal URL
```

#### Service URLs
After deployment, you'll have:
- **Backend API**: `https://shuscribe-backend.railway.app`
- **Portkey Gateway**: `https://shuscribe-portkey.railway.app`
- **Internal Communication**: Services can communicate via Railway's internal networking

## Project Structure for Railway

Your backend directory contains:
- `railway.toml` - Railway configuration
- `Dockerfile` - Container build instructions  
- `pyproject.toml` - Python dependencies
- `.env.railway` - Environment variables template

## Database Migration

### First Deploy
```bash
# SSH into Railway container (after deploy)
railway shell

# Run migrations
uv run alembic upgrade head
```

### Ongoing Deployments
Add to your deployment script or Railway build command:
```bash
uv run alembic upgrade head && uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

## Frontend Integration

Update your Vercel frontend to use Railway backend:
```javascript
// In your frontend .env.local
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## Monitoring

- Railway provides logs and metrics dashboard
- Health check endpoint: `https://your-backend.railway.app/health`
- API documentation: `https://your-backend.railway.app/docs`

## Cost Optimization

### Two-Service Architecture Costs
- **Railway Free Tier**: $5/month credit
- **FastAPI Backend**: ~$5-15/month (based on CPU/memory usage)
- **Portkey Gateway**: ~$5-10/month (lightweight service)
- **Total Estimated**: $10-25/month for both services

### Cost-Saving Tips
- Use Supabase for database (Railway PostgreSQL adds ~$5/month)
- Portkey Gateway is lightweight - use smaller instance size
- FastAPI backend scales with usage - optimize code for efficiency
- Monitor Railway metrics to adjust resource allocation

## Troubleshooting

### Service Communication Issues
```bash
# Check if services can communicate
railway logs --service shuscribe-backend
railway logs --service shuscribe-portkey

# Test Portkey health from backend
curl https://shuscribe-portkey.railway.app/health
```

### Environment Variable Issues
```bash
# List all variables for a service
railway variables --service shuscribe-backend

# Update PORTKEY_BASE_URL if needed
railway variables set PORTKEY_BASE_URL=https://shuscribe-portkey.railway.app/v1 --service shuscribe-backend
```

### Deployment Issues
```bash
# Redeploy a specific service
railway redeploy --service shuscribe-backend

# Check build logs
railway logs --build --service shuscribe-backend
```