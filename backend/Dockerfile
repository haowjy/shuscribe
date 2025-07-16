# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv - copy both uv and uvx for completeness
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set uv environment variables for production optimization
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with cache mount for faster builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-cache

# Copy source code
COPY . .

# Create temp directory for file storage
RUN mkdir -p temp

# Expose port
EXPOSE 8000

# Start the application - use Railway's exact hypercorn pattern
CMD ["hypercorn", "src.main:app", "--bind", "::"]