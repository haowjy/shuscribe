<!-- README.md -->
# ShuScribe

An intelligent platform that automatically generates a personal, spoiler-free wiki for any serialized fiction narrative.

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- [Node.js](https://nodejs.org/) (v18 or higher)
- [pnpm](https://pnpm.io/installation) (package manager for frontend)
- [Git](https://git-scm.com/)

### Manual Setup

1.  **Clone the project:**
    ```bash
    git clone https://github.com/haowjy/shuscribe
    cd shuscribe
    ```
2.  **Configure Environment Variables:**
    ```bash
    cp .env.example .env
    ```
    Now, **edit the `.env` file** in the project root and replace the placeholder values.
    *   `ENCRYPTION_KEY`: Generate a secure 32-character (or longer) key using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
    *   `PORTKEY_BASE_URL`: For local development, this will typically be `http://localhost:8787/v1` after starting your Docker services.

3.  **Backend setup:**
    ```bash
    cd backend
    uv sync
    cd ..
    ```

4.  **Frontend setup:**
    ```bash
    cd frontend
    pnpm install
    cd ..
    ```

5.  **Start all core services (Portkey Gateway & PostgreSQL):**
    ```bash
    docker-compose up -d
    ```
    This will start your self-hosted Portkey Gateway (at `http://localhost:8787`) and your PostgreSQL database.

6.  **Run database migrations:**
    ```bash
    cd backend
    uv run alembic upgrade head
    cd ..
    ```

## 🖥️ VS Code Configuration (for Development)

For the best development experience with this monorepo in VS Code, set up a Multi-Root Workspace. This allows you to work on both frontend and backend concurrently within a single VS Code window.

1.  **Open the entire `shuscribe` monorepo as a Multi-Root Workspace:**
    *   Go to `File > Open Folder...` and select your top-level `shuscribe` directory.
    *   Then, go to `File > Add Folder to Workspace...` and add the `backend` folder.
    *   Repeat `File > Add Folder to Workspace...` and add the `frontend` folder.
    *   (Optional, but good practice) Save your workspace: `File > Save Workspace As...` (e.g., `shuscribe.code-workspace`) in the root `shuscribe` directory. From now on, open this `.code-workspace` file.

2.  **Install Recommended Extensions:**
    *   Ensure you have the "Python" extension (Microsoft) installed.
    *   Ensure you have the "ESLint" extension installed for frontend.
    *   Consider "Docker" and "Tailwind CSS IntelliSense" for additional support.

## 🏗️ Project Structure

```
shuscribe/
├── README.md
├── docker-compose.yml          # Defines the local development environment services (Portkey Gateway, PostgreSQL)
├── .env.example               # Template for project-wide environment variables
├── .gitignore
├── shuscribe.code-workspace   # VS Code Multi-Root Workspace configuration
│
├── backend/                   # FastAPI application for server-side logic
│   ├── pyproject.toml        # Defines backend dependencies and project configuration (uv)
│   ├── uv.lock               # Locks backend dependency versions for reproducible installs
│   ├── src/                  # Backend application source code
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── database/         # Database-related code
│   │   │   ├── connection.py # Establishes database connections
│   │   │   └── models.py     # SQLAlchemy ORM models defining database schema
│   │   ├── api/              # API endpoint definitions
│   │   │   └── routes/       # Individual API route modules
│   │   │       ├── stories.py # API endpoints for story management
│   │   │       └── wiki.py    # API endpoints for wiki article management
│   │   └── services/         # Business logic and services
│   │       └── story_processor.py  # Handles LLM (Large Language Model) pipeline logic
│   ├── migrations/           # Alembic scripts for database schema migrations
│   ├── tests/                # Backend unit and integration tests
│   ├── Dockerfile            # Defines how to build the backend Docker image
│   └── README.md             # Backend-specific documentation
│
├── frontend/                 # Next.js application for the user interface
│   ├── package.json          # Defines frontend dependencies and scripts
│   ├── next.config.js        # Next.js framework configuration
│   ├── tailwind.config.js    # Tailwind CSS framework configuration
│   ├── src/                  # Frontend application source code
│   │   ├── app/              # Next.js App Router for page-based routing and layouts
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── reading/      # Components/pages related to reading view
│   │   │   └── wiki/         # Components/pages related to wiki view
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ui/           # Generic UI components
│   │   │   ├── reading/      # UI components specific to reading view
│   │   │   └── wiki/         # UI components specific to wiki view
│   │   └── lib/              # Utility functions and API client configurations
│   ├── public/               # Static assets served directly by Next.js
│   ├── Dockerfile            # Defines how to build the frontend Docker image
│   └── README.md             # Frontend-specific documentation
│
├── database/                 # Database configuration and custom setups
│   ├── init.sql            # SQL script for initial database schema setup
│   └── docker/             # Docker configurations specific to the database
│       └── Dockerfile      # Custom Dockerfile for PostgreSQL with extensions (e.g., pgvector)
│
└── scripts/                  # Helper scripts for development and prototyping
    ├── dev-setup.sh        # Script for setting up the development environment
    └── prototype.py        # Script for testing LLM pipeline prototypes
```

## 🔧 Development Workflow

### Starting the Development Environment

```bash
# Start all services (Portkey Gateway, database) defined in docker-compose.yml
# Frontend/Backend app servers are run locally for hot-reloading
docker-compose up -d

# View combined logs of all running services
docker-compose logs -f

# Stop all services
docker-compose down
```

### Working with the Backend

```bash
cd backend

# Install/update dependencies
uv sync

# Configure Python Interpreter in VS Code (if not already done via workspace setup)
# 1. Open a Python file (e.g., src/main.py)
# 2. Press Ctrl+Shift+P (or Cmd+Shift+P) and search for "Python: Select Interpreter"
# 3. Choose the interpreter located at `.venv/bin/python` (Linux/macOS) or `.venv/Scripts/python.exe` (Windows) within your backend folder.

# Run backend locally (outside Docker, with hot-reloading)
uv run hypercorn src.main:app --reload --bind "[::]:8000"

# Run tests
uv run pytest

# Create new database migration (after changes to src/database/models.py)
uv run alembic revision --autogenerate -m "Add new table"

# Apply database migrations
uv run alembic upgrade head

# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

### Working with the Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server (with hot-reloading)
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Add new dependency
pnpm add package-name
```

### Database Operations

```bash
# Connect to database (from project root)
docker-compose exec postgres psql -U postgres -d shuscribe

# Backup database (from project root)
docker-compose exec postgres pg_dump -U postgres shuscribe > backup.sql

# Restore database (from project root)
docker-compose exec -T postgres psql -U postgres shuscribe < backup.sql
```

## 🧪 Testing the LLM Pipeline

Before building the full application, test the core LLM functionality:

```bash
# Ensure your Portkey Gateway is running via `docker-compose up -d`
# Then, from the backend directory:
cd backend
uv run python -m src.services.llm.llm_service # Or your specific testing script
```

### Make sure the Portkey Gateway is running

```bash
docker run -d \
  --name portkey-gateway \
  -p 8787:8787 \
  portkeyai/gateway:latest
```

## 📡 API Endpoints

### Core
-   `GET /` - Root API endpoint
-   `GET /health` - Global application health check
-   `GET /api/v1/health/ping` - API v1 health ping

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

## 🌐 Service URLs

When running locally:
-   **Frontend**: `http://localhost:3001`
-   **Backend API**: `http://localhost:8000`
-   **Backend API Docs (Swagger UI)**: `http://localhost:8000/docs`
-   **Self-hosted Portkey Gateway Console**: `http://localhost:8787/public/`
-   **PostgreSQL Database**: `localhost:5432`

## 🏗️ Development Phases

### Phase 1: Core Foundation (Current)
-   [x] Project setup
-   [x] Basic database schema (models, connection, base)
-   [x] Core configuration (settings, constants, exceptions)
-   [x] LLM service integration (Portkey self-hosted)
-   [x] Base API setup (main, router, health endpoints)
-   [x] User authentication (Supabase)
-   [ ] Initial API endpoints (user, story upload placeholder)

### Phase 2: MVP Backend
-   [ ] Full API for Story upload and chapter management
-   [ ] Background processing pipeline (worker, tasks, queue) for LLM analysis
-   [ ] Wiki article generation logic
-   [ ] Progress tracking API

### Phase 3: MVP Frontend
-   [ ] Reading mode interface
-   [ ] Wiki mode interface
-   [ ] Interactive entity popovers
-   [ ] User progress management UI

### Phase 4: Polish & Deploy
-   [ ] Comprehensive testing (unit, integration)
-   [ ] Optimization for performance
-   [ ] Production deployment strategy (e.g., Kubernetes, dedicated VMs)
-   [ ] User feedback and iteration

## 🚀 Deployment

### Local Production Build
```bash
# NOTE: Requires a `docker-compose.prod.yml` which is not yet defined.
# This file would typically include optimizations for production (e.g., no hot-reloading,
# optimized builds, gunicorn for FastAPI, etc.)

# Build all services (from project root)
docker-compose -f docker-compose.prod.yml build

# Run production stack (from project root)
docker-compose -f docker-compose.prod.yml up -d
```

### Database Migrations in Production
```bash
# Run migrations on the deployed backend service (from project root)
docker-compose exec backend uv run alembic upgrade head
```

## 🤝 Contributing

This is currently a solo hobby project, but suggestions and feedback are welcome!

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## 🆘 Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Ensure PostgreSQL is running (from project root)
docker-compose ps

# Check database logs (from project root)
docker-compose logs postgres
```

**Backend import errors / VS Code not recognizing dependencies:**
```bash
# Ensure you're in the backend directory
cd backend

# Reinstall dependencies
uv sync

# Ensure VS Code's Python interpreter is correctly set for the 'backend' folder
# (See "VS Code Configuration" section above)
```

**Frontend build errors:**
```bash
# Ensure you're in the frontend directory
cd frontend

# Clear Next.js cache
rm -rf .next
pnpm build
```

**Portkey Gateway not reachable:**
```bash
# Ensure the gateway container is running (from project root)
docker-compose ps

# Check gateway logs (from project root)
docker-compose logs portkey-gateway

# Verify connectivity
curl http://localhost:8787/health
```

## 📊 Tech Stack

-   **Backend**: FastAPI, SQLAlchemy, PostgreSQL, uv, `cryptography`, Portkey (self-hosted)
-   **Frontend**: Next.js, TypeScript, Tailwind CSS, ESLint
-   **Database**: PostgreSQL with `pgvector`
-   **AI/ML**: OpenAI GPT, Anthropic Claude, Google Gemini (via Portkey Gateway)
-   **DevOps**: Docker, Docker Compose
-   **Authentication**: Supabase Auth (planned)
