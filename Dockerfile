FROM python:3.11-slim

# Install system deps needed by psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev group)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create storage dir (uploads volume mount target)
RUN mkdir -p storage/uploads

EXPOSE 8000

# Run migrations, seed demo data, then start server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run python -m app.seed && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
