# Backend stage
FROM python:3.11-slim

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY pyproject.toml .

# Install uv and dependencies
RUN pip install uv
RUN uv pip install -r pyproject.toml --system

# Copy backend code - ensure we copy the entire app directory structure
COPY . .

# # Final stage
# FROM python:3.11-slim

# WORKDIR /app

# # Copy backend from backend stage
# COPY --from=backend /app/backend /app/backend

# Set environment variables
# ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000
# EXPOSE 3000

# Run the application
CMD ["sh", "-c", "cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]