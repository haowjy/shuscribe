# General Technical Overview

### 1. Technical Vision & Philosophy

ShuScribe is built on a modern, decoupled architecture designed for scalability, maintainability, and a seamless user experience. Our core philosophy is to separate concerns, allowing each component of the system to excel at its specific task while ensuring our intellectual property remains secure.

The architecture is guided by these key principles:
*   **Asynchronous First:** Resource-intensive operations are executed in the background to ensure the user-facing application remains fast and responsive.
*   **Flexible Data Storage:** Support both persistent database storage (via Supabase) for web deployment and in-memory storage for local/CLI usage.
*   **Secure Backend Logic:** All proprietary prompts and processing logic are kept securely on the backend, never exposed to the client.
*   **User-Funded Processing (BYOK):** For the MVP, users provide their own API keys, which are used by our secure backend for processing. This removes LLM costs and scaling risks while setting a clear path for future premium tiers.
*   **Deployment Flexibility:** Support both cloud-based web service and local CLI/API operation to accommodate different user needs.

### 2. High-Level System Architecture

The system supports two primary deployment modes with shared core logic:

#### 2.1 Web Deployment Architecture

```
                                                              ┌──────────────────┐
                                                              │ External LLM     │
                                                              │ Services         │
                                                              └─────────▲────────┘
                                                                        │
┌──────────────┐   (Static HTML,    ┌───────────────────────────────────┴───────────────────────────────────┐
│ User/Browser │◀─── JS Bundle) ───▶│                      ShuScribe Backend System                         │
└───────▲──────┘                     │                                                                       │
        │ (JWT Auth)                 │ ┌──────────────────┐   (Enqueue Task)   ┌───────────────────────────┐ │
        │                            │ │ FastAPI Web Server │───────────────────▶│  Background Processing    │ │
        │                            │ └─────────▲────────┘                    │  (Workers & Queue)        │ │
        │                            │           │ (Verify JWT)                └────────────┬────────────┘ │
┌───────┴──────┐                     │           │                                          │              │
│ Supabase Auth│◀────────────────────┘           └──────────────────┬───────────────────────┘              │
└──────────────┘                                                    │ (Supabase Client)                   │
                                                                    ▼                                     │
                                                              ┌──────────────┐                            │
                                                              │ Supabase DB  │                            │
                                                              │(w/ user keys)│                            │
                                                              └──────────────┘                            │
                                                                                                          │
                               └──────────────────────────────────────────────────────────────────────────┘
```

#### 2.2 Local/CLI Deployment Architecture

```
                                         ┌──────────────────┐
                                         │ External LLM     │
                                         │ Services         │
                                         └─────────▲────────┘
                                                   │
┌──────────────┐   (Direct API calls)   ┌─────────┴─────────────────────────────────────┐
│ CLI/API User │◀──────────────────────▶│           ShuScribe Backend API              │
└──────────────┘                        │                                             │
                                        │ ┌──────────────────┐   (Sync Processing)  │
                                        │ │ FastAPI Server   │◀──────────────────────┤
                                        │ └─────────▲────────┘                      │
                                        │           │ (Repository Pattern)          │
                                        │           ▼                               │
                                        │ ┌──────────────────┐                      │
                                        │ │ In-Memory        │                      │
                                        │ │ Repositories     │                      │
                                        │ └──────────────────┘                      │
                                        └───────────────────────────────────────────┘
```

### 3. Component Breakdown

#### 3.1 Core Components (Shared)

*   **FastAPI Backend:** The unified API server supporting both deployment modes.
    *   **Role:** Handles all HTTP requests, manages processing logic, and orchestrates LLM interactions.
    *   **Features:** Health checks, user management, story processing, wiki generation APIs.
    *   **Repository Pattern:** Uses abstract repositories that can be backed by either Supabase or in-memory storage.

*   **Repository Layer:** Abstracted data access supporting multiple backends.
    *   **Supabase Repository:** For web deployment with persistent storage, user accounts, and progress tracking.
    *   **In-Memory Repository:** For local/CLI usage with temporary storage and no user accounts required.

*   **LLM Integration:** Secure handling of user API keys and external LLM communication.
    *   **Key Management:** Encrypted storage (Supabase) or secure in-memory handling (local).
    *   **Provider Support:** Unified interface for multiple LLM providers (OpenAI, Anthropic, etc.).

#### 3.2 Web Deployment Specific

*   **Next.js Frontend (Planned):** The user's primary web interface.
    *   **Role:** Renders the UI, provides settings for API key management, and initiates content uploads.
    *   **Authentication:** Integrates with Supabase Auth for user management.

*   **Supabase Integration:** Cloud database and authentication service.
    *   **Database:** Stores users, stories, chapters, wiki articles, and encrypted API keys.
    *   **Authentication:** Manages user sessions and security.

*   **Background Processing (Planned):** Asynchronous task processing for web scalability.
    *   **Role:** Handles long-running wiki generation tasks without blocking the web interface.

#### 3.3 Local/CLI Deployment Specific

*   **CLI Interface (Planned):** Command-line tools for local story processing.
    *   **Role:** Direct file input, processing commands, and output generation.
    *   **Storage:** All data kept in memory during processing, optionally exported to files.

*   **API-Only Mode:** Direct API access without web interface.
    *   **Role:** Programmatic access for developers and custom integrations.
    *   **Processing:** Synchronous processing suitable for single-user, local operation.

### 4. Current Implementation Status

#### ✅ Completed
*   **Core API Infrastructure:** FastAPI application with health endpoints and basic routing
*   **Configuration System:** Environment-based configuration supporting both deployment modes
*   **Repository Pattern:** Abstract repository interfaces with both Supabase and in-memory implementations
*   **User Management:** Complete schemas and repository implementations for user and API key management
*   **Supabase Integration:** Connection management and repository implementation
*   **Error Handling:** Custom exception hierarchy and global error handling
*   **Security Framework:** Encryption utilities and basic security infrastructure

#### 🔄 In Development
*   **Service Layer:** Business logic services (story, wiki, progress) - structure implemented, logic pending
*   **LLM Pipeline:** Story processing and wiki generation algorithms
*   **Background Processing:** Task queue and worker implementation for web deployment

#### ❌ Planned
*   **Frontend UI:** Next.js web interface
*   **CLI Tools:** Command-line interface for local usage
*   **Advanced Pipeline:** Complete wiki generation with entity extraction and linking
*   **Authentication:** Full user authentication and authorization system

### 5. Key Workflow: Flexible BYOK Model

The system supports two main workflows depending on deployment mode:

#### 5.1 Web Deployment Workflow

**One-Time Setup:**
1. User registers via Supabase Auth
2. User enters API key through web interface
3. Key is encrypted and stored in Supabase database

**Processing:**
1. User uploads story through web interface
2. Content stored in Supabase database
3. Background task queued for processing
4. Worker retrieves content and encrypted key
5. Wiki generated and stored back to database

#### 5.2 Local/CLI Workflow

**Setup:**
1. User provides API key via environment variable or configuration
2. Key stored securely in memory during processing

**Processing:**
1. User submits story via CLI command or API call
2. Content processed immediately in memory
3. LLM calls made using provided API key
4. Results returned directly or exported to files

### 6. Technology Stack

#### Backend Core
*   **Framework:** FastAPI (Python 3.12+)
*   **Package Manager:** uv for fast dependency management
*   **Configuration:** Pydantic Settings with environment variable support
*   **Validation:** Pydantic schemas for all data models

#### Data Storage
*   **Web Mode:** Supabase (PostgreSQL + Auth + Real-time)
*   **Local Mode:** In-memory Python dictionaries with persistence options
*   **Repository Pattern:** Abstract interfaces enabling seamless switching

#### External Integrations
*   **LLM Providers:** Support for OpenAI, Anthropic, Google, and others
*   **Gateway:** Self-hosted Portkey Gateway for unified LLM access
*   **Authentication:** Supabase Auth (web mode only)

#### Development & Deployment
*   **Containerization:** Docker support for consistent deployment
*   **Environment Management:** Flexible configuration for different deployment scenarios
*   **Testing:** Pytest framework with async support

