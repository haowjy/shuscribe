<!-- backend/README.md -->

# ShuScribe Backend API

This directory contains the FastAPI backend application for ShuScribe, a **Universe Content Management Platform** built for writers and creators to manage complex fictional universes at any scale.

## 🌟 Overview

The ShuScribe Backend provides the API endpoints and server-side logic for a comprehensive content management platform, including:

-   **Project Management**: Create and manage writing projects with hierarchical organization
-   **Document System**: Full-featured document management with ProseMirror content
-   **File Tree Management**: VS Code-like file explorer with folder/file organization
-   **Tag System**: Advanced tagging with many-to-many relationships and categorization
-   **Authentication**: Secure user authentication via Supabase Auth
-   **Repository Pattern**: Clean architecture with SQLAlchemy ORM and repository interfaces

Built with a **frontend-first philosophy** where the backend implements APIs to match frontend TypeScript interfaces, ensuring seamless integration and type safety.

## ✨ Key Features

-   **Project Management**: Create, update, and organize writing projects with metadata and settings
-   **Document Management**: Full CRUD operations for documents with ProseMirror content support
-   **File Tree System**: Hierarchical file/folder organization with drag-and-drop support
-   **Advanced Tag System**: Many-to-many tagging with categories, colors, icons, and usage analytics
-   **Supabase Authentication**: Secure JWT-based authentication with user session management
-   **Repository Pattern**: Clean separation of concerns with interfaces and implementations
-   **Database Seeding**: Automated development data generation with configurable templates
-   **PostgreSQL Integration**: Full async SQLAlchemy ORM with proper relationships and constraints
-   **Health & Monitoring**: Comprehensive health checks and application monitoring
-   **Self-hosted LLM Gateway**: Future AI integration via Portkey Gateway (planned)

## 🚀 Getting Started

These instructions assume you have already followed the **main `shuscribe/README.md`** for the overall monorepo setup, including starting the `docker-compose` services (PostgreSQL).

### Prerequisites

-   **Python 3.12+**
-   **uv** (Python package manager, installed globally as per main README)
-   **PostgreSQL Database**: Running via Docker Compose from project root
-   **Supabase Project**: For authentication (see main README for setup)
-   **Encryption Key**: Generate using: `uv run python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 1. Navigate to the Backend Directory

```bash
cd shuscribe/backend
```

### 2. Create your `.env` File

Copy the provided example environment variables:

```bash
cp .env.example .env
```

Now, **edit the `.env` file** in this `backend/` directory. It should look like the `backend/.env.example` shown above.

**Important Notes for `.env`:**
-   **`SECRET_KEY`**: Generate a strong, unique key for JWT authentication
-   **`ENCRYPTION_KEY`**: Set this to your unique 32-byte key generated from prerequisites
-   **`DATABASE_URL`**: PostgreSQL connection string with `postgresql+asyncpg://` driver
-   **`SUPABASE_URL`**: Your Supabase project URL for authentication
-   **`SUPABASE_ANON_KEY`**: Supabase anonymous key for client authentication
-   **`ALLOWED_ORIGINS`**: CORS origins as JSON array, e.g., `'["http://localhost:3001"]'`

**Database Seeding Configuration:**
-   **`ENABLE_DATABASE_SEEDING`**: Set to `true` to enable automatic seeding on startup
-   **`SEED_DATA_SIZE`**: Control dataset size: `small`, `medium`, or `large`
-   **`CLEAR_BEFORE_SEED`**: Set to `true` to force-clear and reseed existing data
-   **`TABLE_PREFIX`**: Prefix for all database tables (default: `test_` for development)

### 3. Install Python Dependencies

Use `uv` to install all required packages:

```bash
uv sync
```

### 4. Database Setup

The backend uses a **no-migrations approach** with automatic table creation. Ensure your PostgreSQL container is running (via `docker-compose up -d` from the monorepo root).

**Automatic Setup on First Run:**
- Tables are created automatically when the server starts
- Database seeding runs automatically if configured in `.env`

**Manual Database Seeding:**
```bash
# Seed with sample data
uv run python scripts/seed_database.py --clear --size medium

# Check if database has data
uv run python scripts/seed_database.py --check-only
```

### 5. Run the FastAPI Application

Once dependencies are installed and core Docker services are running:

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables hot-reloading for development.

> **Note**: `uv run` automatically activates the virtual environment and runs the command with the correct Python interpreter and dependencies. No need to manually activate the virtual environment!

### 7. Access the API

Once the server is running locally:

-   **Root API Endpoint**: `http://localhost:8000/`
-   **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
-   **API Documentation (ReDoc)**: `http://localhost:8000/redoc`
-   **Global Health Check**: `http://localhost:8000/health`
-   **API v1 Health Ping**: `http://localhost:8000/api/v1/health/ping`

You can also monitor requests going through your self-hosted Portkey Gateway via its console at `http://localhost:8787/public/`.

## 📁 Project Structure

The `src/` directory follows a clean, layered architecture with repository pattern:

```
src/
├── main.py                 # FastAPI application entry point with automatic seeding
├── config.py               # Application-wide settings and environment variables
│
├── api/                    # API layer (handles requests/responses)
│   ├── dependencies.py     # Common API dependencies (auth, database sessions)
│   └── v1/                 # API versioning
│       ├── router.py       # Main router for API v1
│       └── endpoints/      # API endpoint definitions
│           ├── projects.py # Project management endpoints
│           ├── documents.py# Document CRUD operations
│           ├── tags.py     # Tag management and assignment
│           └── health.py   # Health check endpoints
│
├── schemas/                # Pydantic schemas (data validation, API contracts)
│   ├── base.py             # Base response schemas
│   ├── requests/           # Request body schemas
│   └── responses/          # Response schemas
│
├── database/               # Database interaction layer
│   ├── connection.py       # Async SQLAlchemy engine and session management
│   ├── models.py           # SQLAlchemy ORM models with relationships
│   ├── factory.py          # Repository factory and dependency injection
│   ├── seeder.py           # Database seeding with template-based data generation
│   ├── seed.py             # Mock data factory and project templates
│   ├── interfaces/         # Repository interfaces for clean architecture
│   └── repositories.py     # Repository implementations (database layer)
│
├── services/               # Business logic layer
│   └── auth/               # Authentication services
│       └── supabase_auth.py# Supabase JWT validation
│
├── core/                   # Core application functionalities
│   ├── exceptions.py       # Custom exception classes
│   ├── security.py         # Authentication and authorization
│   ├── middleware.py       # FastAPI middleware (CORS, error handling)
│   ├── logging.py          # Application logging configuration
│   └── constants.py        # Application-wide constants
│
└── utils/                  # General utility functions
    ├── encryption.py       # Encryption utilities
    └── text_processing.py  # Text and content processing
```

## 🧑‍💻 Development Workflow

Assuming you are in the `backend/` directory:

**Core Development:**
-   **Install/update dependencies**: `uv sync`
-   **Run backend locally**: `uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
-   **Run tests**: `uv run pytest`
-   **Add new dependency**: `uv add package-name`
-   **Add development dependency**: `uv add --dev package-name`

**Database Management:**
-   **Seed database**: `uv run python scripts/seed_database.py --clear --size medium`
-   **Check database status**: `uv run python scripts/seed_database.py --check-only`
-   **Force reseed**: `uv run python scripts/seed_database.py --force --clear`

**Code Quality:**
-   **Format code**: `uv run black . && uv run isort .`
-   **Type checking**: `uv run mypy src/` (when configured)
-   **Lint code**: Check with your preferred linter

**Note**: This project uses a **no-migrations approach** with automatic table creation and seeding.

## 📡 API Endpoints

All API endpoints are prefixed with `/api/v1`. View complete documentation at `http://localhost:8000/docs`.

### Core
-   `GET /` - Root API endpoint
-   `GET /health` - Global application health check
-   `GET /api/v1/health/ping` - API v1 health ping

### Projects
-   `GET /api/v1/projects` - List all projects for authenticated user
-   `POST /api/v1/projects` - Create a new project
-   `GET /api/v1/projects/{project_id}` - Get project details
-   `PUT /api/v1/projects/{project_id}` - Update project
-   `DELETE /api/v1/projects/{project_id}` - Delete project

### Documents
-   `GET /api/v1/projects/{project_id}/documents` - List documents in project
-   `POST /api/v1/documents` - Create a new document
-   `GET /api/v1/documents/{document_id}` - Get document with content
-   `PUT /api/v1/documents/{document_id}` - Update document
-   `DELETE /api/v1/documents/{document_id}` - Delete document

### File Tree
-   `GET /api/v1/projects/{project_id}/file-tree` - Get complete file tree structure
-   `POST /api/v1/file-tree/folders` - Create new folder
-   `POST /api/v1/file-tree/files` - Create new file
-   `PUT /api/v1/file-tree/{item_id}` - Update file tree item
-   `DELETE /api/v1/file-tree/{item_id}` - Delete file tree item

### Tags
-   `GET /api/v1/projects/{project_id}/tags` - List all tags in project
-   `POST /api/v1/tags` - Create new tag
-   `PUT /api/v1/tags/{tag_id}` - Update tag
-   `DELETE /api/v1/tags/{tag_id}` - Delete tag
-   `POST /api/v1/tags/assign` - Assign tags to items
-   `DELETE /api/v1/tags/unassign` - Remove tag assignments

## 🚨 Production Considerations

When preparing the backend for production:

1.  **Containerization**: Build the backend Docker image using the `Dockerfile` in this directory.
2.  **Environment Variables**: Ensure all sensitive variables (`SECRET_KEY`, `ENCRYPTION_KEY`, `DATABASE_URL`, `PORTKEY_BASE_URL`) are securely managed (e.g., Kubernetes Secrets, AWS Secrets Manager).
3.  **Scalability**: Use a production-ready ASGI server (like Gunicorn with Uvicorn workers) and deploy behind a load balancer.
4.  **Monitoring & Logging**: Implement robust application monitoring, logging aggregation, and alerting.
5.  **Security Best Practices**: Review for common vulnerabilities (e.g., input validation, secure headers).

## ⚡ Next Steps

Current development priorities:

1.  **Frontend Integration**: Complete integration between frontend and backend tag system
2.  **AI Agent System**: Implement LLM-powered content generation and analysis
3.  **User Permissions**: Add role-based access control for collaborative projects
4.  **Publishing System**: Build export functionality for various publishing formats
5.  **Performance Optimization**: Add caching, query optimization, and background processing
6.  **Comprehensive Testing**: Expand unit and integration test coverage

## 🆘 Troubleshooting

### Common Issues

**Database connection errors:**
-   Ensure PostgreSQL container is running: `docker-compose ps` from project root
-   Verify `DATABASE_URL` in `backend/.env` uses `postgresql+asyncpg://`
-   Check database credentials and connection string format

**Database seeding issues:**
-   Verify seeding configuration in `.env`: `ENABLE_DATABASE_SEEDING=true`
-   Check if database is empty: `uv run python scripts/seed_database.py --check-only`
-   Force reseed: `uv run python scripts/seed_database.py --force --clear`

**Backend import errors:**
-   Ensure you're in the `backend/` directory
-   Run `uv sync` to install all dependencies
-   Check Python interpreter points to `backend/.venv/bin/python`
-   Try `uv sync --reinstall` if issues persist

**FastAPI application not starting:**
-   Check console output for detailed error messages
-   Verify `.env` configuration (especially `SECRET_KEY`, `SUPABASE_URL`)
-   Ensure PostgreSQL container is running
-   Check for port conflicts on 8000

**Authentication issues:**
-   Verify Supabase configuration in `.env`
-   Check `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
-   Ensure frontend and backend Supabase configurations match

### Getting Help

-   Review API documentation at `http://localhost:8000/docs`
-   Check main project README for Docker and environment setup
-   Consult specialized guides in `/frontend/CLAUDE-frontend.md` and `/backend/CLAUDE-backend.md`
