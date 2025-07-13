<!-- backend/README.md -->

# ShuScribe Backend API

This directory contains the FastAPI backend application for ShuScribe, an intelligent platform that automatically generates a personal, spoiler-free wiki for any serialized fiction narrative.

## 🌟 Overview

The ShuScribe Backend is the secure core of the application. It provides the API endpoints for the frontend and handles all server-side logic, including:

-   Securely managing user accounts and user-provided LLM API keys (BYOK - Bring Your Own Key model).
-   Orchestrating the story processing pipeline to generate wiki content.
-   Storing all persistent data (users, stories, chapters, wiki articles, progress) in a PostgreSQL database.
-   Securely interacting with external LLM services via a **self-hosted Portkey Gateway** using the user's API keys.

It's built with a focus on security, scalability, and maintainability, separating concerns into distinct layers (API, Services, Repositories, Models).

## ✨ Key Features

-   **User Account Management**: Manages user registration, authentication, and profiles.
-   **BYOK API Key Management**: Secure storage (encrypted) and on-the-fly decryption of user-provided LLM API keys.
-   **Content Ingestion**: Provides API endpoints for uploading story content (text/files).
-   **Asynchronous Processing**: Queues and executes computationally intensive LLM-based processing tasks in the background.
-   **Self-hosted LLM Gateway Integration**: Routes requests to various LLM providers (OpenAI, Anthropic, Google, etc.) through your own Portkey Gateway instance.
-   **PostgreSQL Database Integration**: Uses SQLAlchemy ORM for robust data management of all application data.
-   **Wiki & Progress API**: Delivers generated wiki content and manages user reading progress.
-   **Health & Status Checks**: Endpoints for monitoring API health.

## 🚀 Getting Started

These instructions assume you have already followed the **main `shuscribe/README.md`** for the overall monorepo setup, including starting the `docker-compose` services (PostgreSQL and Portkey Gateway).

### Prerequisites

-   **Python 3.12+**
-   **uv** (Python package manager, installed globally as per main README)
-   **Cryptography Key**: A 32-character (or longer) random string for symmetric encryption of user API keys. Generate one using: `uv run python -c "import secrets; print(secrets.token_urlsafe(32))"`
-   **`asyncpg`**: The asynchronous PostgreSQL driver. This will be installed via `uv sync`.

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
-   **`SECRET_KEY`**: Generate a strong, unique key for authentication.
-   **`ENCRYPTION_KEY`**: Set this to your unique 32-byte key generated from prerequisites.
-   **`ALLOWED_ORIGINS`**: Crucially, define this as a JSON array string, wrapped in single quotes, e.g., `'["http://localhost:3001", "http://127.0.0.1:3001"]'`
-   **`DATABASE_URL`**: Ensure it starts with `postgresql+asyncpg://` to use the correct asynchronous driver.
-   **`PORTKEY_BASE_URL`**: This should point to your running self-hosted Portkey Gateway (e.g., `http://localhost:8787/v1`).
-   There is **no `PORTKEY_API_KEY`** needed for a self-hosted gateway.

### 3. Install Python Dependencies

Use `uv` to install all required packages:

```bash
uv sync
```

### 4. Apply Database Migrations (using Alembic)

Ensure your PostgreSQL container is running (via `docker-compose up -d` from the monorepo root) before running migrations.

```bash
uv run alembic upgrade head
```

### 5. Make sure the Portkey Gateway is running

```bash
docker run -d \
  --name portkey-gateway \
  -p 8787:8787 \
  portkeyai/gateway:latest
```

### 6. Run the FastAPI Application

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

The `src/` directory within `backend/` follows a clear, layered architecture:

```
src/
├── main.py                 # FastAPI application entry point
├── config.py               # Application-wide settings
│
├── api/                    # API layer (handles requests/responses)
│   ├── dependencies.py     # Common API dependencies (e.g., DB session, auth)
│   └── v1/                 # API versioning
│       ├── router.py       # Main router for API v1
│       └── endpoints/      # Individual API endpoint definitions (users, stories, wiki, health)
│
├── schemas/                # Pydantic schemas (data validation, API contracts)
│
├── database/               # Database interaction layer
│   ├── connection.py       # SQLAlchemy engine and session setup
│   ├── models.py           # SQLAlchemy ORM models (table definitions)
│   ├── base.py             # Base for SQLAlchemy models (for Alembic)
│   └── repositories/       # Data Access Layer (Repository Pattern)
│
├── services/               # Business logic layer
│   ├── story_service.py    # Logic for story processing orchestration
│   ├── wiki_service.py     # Logic for wiki content generation/management
│   ├── user_service.py     # Logic for user accounts and API keys
│   └── llm/                # LLM interaction module (Self-hosted Portkey integration)
│
├── core/                   # Core application functionalities
│   ├── exceptions.py       # Custom exception classes
│   ├── security.py         # Authentication and authorization
│   ├── middleware.py       # FastAPI middleware (e.g., CORS, Rate Limiting)
│   ├── constants.py        # Application-wide constants and enums
│   └── events.py           # Application event handling
│
├── background/             # For background task processing (e.g., Celery/RQ - Future)
│
└── utils/                  # General utility functions (logging, encryption, text processing)
```

## 🧑‍💻 Development Workflow (Backend Specific)

Assuming you are in the `backend/` directory:

-   **Install/update dependencies**: `uv sync`
-   **Run backend locally**: `uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
-   **Run tests**: `uv run pytest`
-   **Create new database migration**: `uv run alembic revision --autogenerate -m "Your descriptive message"` (after changes to `src/database/models.py`)
-   **Apply database migrations**: `uv run alembic upgrade head`
-   **Add new dependency**: `uv add package-name`
-   **Add development dependency**: `uv add --dev package-name`
-   **Type checking**: `uv run mypy src/`
-   **Lint/Format code**: `uv run black .` `uv run isort .`

## 📡 API Endpoints

All API endpoints are prefixed with `/api/v1`.

### Core
-   `GET /` - Root API endpoint
-   `GET /health` - Global application health check
-   `GET /api/v1/health/ping` - API v1 health ping

### LLM Catalog & Configuration (UPDATED)
-   `GET /api/v1/llm/families` - Get all abstract AI model families and their inherent capabilities.
-   `GET /api/v1/llm/providers` - Get all LLM providers and their specific hosted model instances.
-   `GET /api/v1/llm/providers/{provider_id}/models` - Get hosted model instances for a specific LLM provider.

### Stories
-   `POST /api/v1/stories` - Upload a new story
-   `GET /api/v1/stories/{story_id}` - Get story details
-   `GET /api/v1/stories/{story_id}/chapters` - Get story chapters

### Wiki
-   `GET /api/v1/stories/{story_id}/wiki` - Get all wiki articles for a story
-   `GET /api/v1/stories/{story_id}/wiki/{slug}` - Get a specific wiki article by slug

### Progress
-   `POST /api/v1/progress` - Update reading progress for a user on a story
-   `GET /api/v1/progress/{story_id}` - Get current reading progress for a user on a story

## 🚨 Production Considerations

When preparing the backend for production:

1.  **Containerization**: Build the backend Docker image using the `Dockerfile` in this directory.
2.  **Environment Variables**: Ensure all sensitive variables (`SECRET_KEY`, `ENCRYPTION_KEY`, `DATABASE_URL`, `PORTKEY_BASE_URL`) are securely managed (e.g., Kubernetes Secrets, AWS Secrets Manager).
3.  **Scalability**: Use a production-ready ASGI server (like Gunicorn with Uvicorn workers) and deploy behind a load balancer.
4.  **Monitoring & Logging**: Implement robust application monitoring, logging aggregation, and alerting.
5.  **Security Best Practices**: Review for common vulnerabilities (e.g., input validation, secure headers).

## ⚡ Next Steps (Backend Focused)

Current immediate backend development tasks include:

1.  **Implement Authentication**: Integrate with Supabase for user authentication and authorization.
2.  **User API Key Endpoints**: Create endpoints for users to manage their BYOK LLM keys.
3.  **Story Upload Logic**: Develop the full logic for story content ingestion via the API.
4.  **Background Processing Integration**: Set up a background task queue (e.g., Celery/RQ) to offload LLM processing.
5.  **LLM Pipeline Development**: Implement the full wiki generation and entity extraction logic within the `services/llm/pipeline.py` and `services/llm/processors/`.
6.  **Comprehensive Testing**: Write unit and integration tests for all backend services and endpoints.

## 🆘 Troubleshooting (Backend Specific)

### Common Issues

**Database connection errors:**
-   Ensure the PostgreSQL container is running via `docker-compose ps` from the monorepo root.
-   Verify your `DATABASE_URL` in `backend/.env` is correct.

**Backend import errors / VS Code not recognizing dependencies:**
-   Ensure you are in the `backend/` directory (`cd backend`).
-   Run `uv sync` to ensure all dependencies are installed.
-   Verify your VS Code Python interpreter is set to the `backend/.venv/bin/python` created by `uv`.
-   If still having issues, try `uv sync --reinstall` to force reinstallation.

**FastAPI application not starting:**
-   Check the console output for error messages.
-   Verify your `.env` file is correctly configured (especially `SECRET_KEY`, `ENCRYPTION_KEY`, `PORTKEY_BASE_URL`).
-   Ensure the Portkey Gateway and PostgreSQL database containers are running (`docker-compose ps`).

**LLM requests failing:**
-   Ensure your `PORTKEY_BASE_URL` in `backend/.env` is correct and the Portkey Gateway is running (`http://localhost:8787/health` should respond).
-   Check the Portkey Gateway console (`http://localhost:8787/public/`) for detailed LLM request logs and errors.
-   Verify the user's provided LLM API key (e.g., OpenAI, Anthropic) is valid.

### Getting Help

-   Review the full Backend API documentation at `http://localhost:8000/docs`.
-   Consult the main `shuscribe/README.md` for overall project setup and Docker troubleshooting.
-   Check the project's [Issues](https://github.com/haowjy/shuscribe/issues) page.
