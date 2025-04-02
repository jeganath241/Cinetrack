# Backend stage
# FROM python:3.11-slim as backend

# WORKDIR /app/backend

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Copy dependency files first
# COPY pyproject.toml .

# # Install uv and dependencies
# RUN pip install uv
# RUN uv pip install -r pyproject.toml --system

# Copy backend code - ensure we copy the entire app directory structure
# COPY backend/app ./app
# COPY backend/main.py .

# Frontend stage
FROM node:18-alpine as frontend

WORKDIR /app/frontend

# Set npm configuration
# RUN npm config set registry https://registry.npmjs.org/ \
#     && npm config set strict-ssl false \
#     && npm config set legacy-peer-deps true

# Copy package files
COPY frontend/package*.json ./

# Clean install dependencies
# RUN rm -rf node_modules package-lock.json
# RUN npm cache clean --force

# Install dependencies and Vite globally
RUN npm install -g vite
RUN npm install

# Copy the rest of the frontend code
COPY frontend/ .

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy backend from backend stage
COPY --from=backend /app/backend /app/backend

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000
EXPOSE 3000

# Run the application
CMD ["sh", "-c", "cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
