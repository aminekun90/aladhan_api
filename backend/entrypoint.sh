#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Run Migrations
echo "🚀 Running Database Migrations..."
uv run alembic upgrade head

# 2. Start the Server
echo "🚀 Starting Uvicorn..."
# 'exec' replaces the shell process with uvicorn, handling signals correctly
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000