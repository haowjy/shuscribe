# ShuScribe Deployment Guide

This guide covers production deployment of ShuScribe's frontend-backend architecture.

## Overview

ShuScribe uses a **distributed deployment strategy** optimized for performance and cost:

- **Frontend**: Vercel (Next.js 15 + React 19)
- **Backend**: Railway (FastAPI + Portkey Gateway)
- **Database**: Supabase (PostgreSQL with pgvector)
- **Authentication**: Supabase Auth
- **LLM Gateway**: Self-hosted Portkey on Railway

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Vercel        │    │   Railway       │    │   Supabase      │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Next.js)     │    │   (FastAPI)     │    │   (PostgreSQL)  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │                 │
                       │   Railway       │
                       │   Portkey       │
                       │   (LLM Gateway) │
                       │                 │
                       └─────────────────┘
```

## Deployment Steps

### 1. Database Setup (Supabase)

```bash
# 1. Create Supabase project at https://supabase.com
# 2. Enable necessary extensions
# 3. Configure authentication providers
# 4. Set up Row Level Security (RLS) policies
# 5. Get connection credentials
```

**Required Supabase Configuration:**
- Enable `pgvector` extension for vector operations
- Configure OAuth providers (Google, GitHub, etc.)
- Set up redirect URLs for your Vercel domain
- Configure RLS policies for data security

### 2. Backend Deployment (Railway)

See detailed guide: [`/backend/railway-deploy.md`](../../backend/railway-deploy.md)

**Two-Service Architecture:**
1. **FastAPI Backend Service** - Main application logic
2. **Portkey Gateway Service** - LLM request routing

**Key Environment Variables:**
```bash
# Backend Service
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SUPABASE_URL=https://your-project.supabase.co
PORTKEY_BASE_URL=https://shuscribe-portkey.railway.app/v1
ALLOWED_ORIGINS=["https://your-app.vercel.app"]

# Portkey Service  
NODE_ENV=production
PORT=8787
```

### 3. Frontend Deployment (Vercel)

```bash
# 1. Connect GitHub repository to Vercel
# 2. Set build settings
# 3. Configure environment variables
# 4. Deploy
```

**Vercel Configuration:**
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

**Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://shuscribe-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Security Configuration

### CORS Setup
Configure allowed origins in backend:
```python
ALLOWED_ORIGINS = [
    "https://your-production-domain.com",
    "https://your-app.vercel.app",
    "https://custom-domain.com"  # If using custom domain
]
```

### API Key Management
- LLM API keys stored encrypted in backend
- Supabase handles authentication tokens
- Environment variables never exposed to frontend

### Database Security
- Row Level Security (RLS) enabled
- User isolation through Supabase Auth
- Encrypted connections (SSL/TLS)

## Monitoring and Logging

### Railway Monitoring
- Built-in metrics dashboard
- Real-time logs for both services
- Resource usage tracking
- Health check endpoints

### Vercel Analytics
- Core Web Vitals monitoring
- Function execution logs
- Build and deployment logs
- Performance insights

### Custom Monitoring
```python
# Backend health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": await check_database_connection(),
            "portkey": await check_portkey_connection()
        }
    }
```

## Performance Optimization

### Frontend (Vercel)
- Automatic CDN distribution
- Edge function deployment
- Image optimization
- Static generation where possible

### Backend (Railway)
- Container auto-scaling
- Connection pooling for database
- Async request handling
- Efficient dependency management with `uv`

### Database (Supabase)
- Connection pooling enabled
- Read replicas for scaling
- Automatic backups
- Point-in-time recovery

## Cost Optimization

### Monthly Cost Breakdown
```
Vercel (Hobby):     $0/month (free tier)
Railway:            $10-25/month (two services)
Supabase:           $0-25/month (based on usage)
Total:              $10-50/month
```

### Cost-Saving Strategies
- Use Vercel free tier for frontend
- Optimize Railway resource allocation
- Use Supabase free tier initially
- Monitor usage and scale appropriately

## Backup and Disaster Recovery

### Database Backups
- Supabase automatic daily backups
- Point-in-time recovery available
- Export capabilities for migration

### Application Backups
- Code stored in GitHub (version control)
- Environment variables documented
- Infrastructure as code approach

### Recovery Procedures
1. **Database Recovery**: Restore from Supabase backup
2. **Backend Recovery**: Redeploy from GitHub to Railway
3. **Frontend Recovery**: Redeploy from GitHub to Vercel
4. **Configuration Recovery**: Restore environment variables

## CI/CD Pipeline

### GitHub Actions Setup
```yaml
# .github/workflows/deploy.yml
name: Deploy ShuScribe
on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railway-app/railway@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
          service: shuscribe-backend

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

## Troubleshooting

### Common Issues

#### CORS Errors
```bash
# Check allowed origins in backend
railway variables --service shuscribe-backend | grep ALLOWED_ORIGINS

# Update if needed
railway variables set ALLOWED_ORIGINS='["https://your-app.vercel.app"]' --service shuscribe-backend
```

#### Database Connection Issues
```bash
# Test database connection
railway shell --service shuscribe-backend
uv run python -c "from src.database.connection import test_connection; test_connection()"
```

#### Service Communication Issues
```bash
# Test Portkey connectivity
curl https://shuscribe-portkey.railway.app/health

# Check logs
railway logs --service shuscribe-backend --tail 100
```

### Performance Issues
- Monitor Railway metrics for resource usage
- Check Vercel function execution times
- Review database query performance in Supabase

## Scaling Considerations

### Traffic Growth
- Railway auto-scales based on demand
- Vercel edge functions handle traffic spikes
- Supabase connection pooling manages database load

### Feature Scaling
- Add Railway services as needed
- Use Vercel edge functions for real-time features
- Consider read replicas for database scaling

### Geographic Scaling
- Vercel global CDN automatic
- Railway multi-region deployment available
- Supabase global distribution options

---

For detailed service-specific deployment instructions:
- **Railway Backend**: [`/backend/railway-deploy.md`](../../backend/railway-deploy.md)
- **Frontend Setup**: [`/frontend/CLAUDE-frontend.md`](../../frontend/CLAUDE-frontend.md)
- **API Documentation**: [`/_docs/core/api-reference.md`](../core/api-reference.md)