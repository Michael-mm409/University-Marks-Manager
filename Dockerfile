#############################
# Stage 1: Build Tailwind CSS
#############################
FROM node:20-alpine AS tailwind

WORKDIR /build

# Copy only what's needed to compile tailwind
COPY package.json ./
COPY tailwind.config.js ./
COPY src/static/css/input.css ./src/static/css/input.css
COPY src/templates ./src/templates
COPY src/presentation/web ./src/presentation/web

# Install deps and compile CSS (use npm ci when lockfile present, otherwise install)
RUN npm install && \
    npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/tailwind.css --minify

#############################
# Stage 2: Python runtime
#############################
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build dependencies for psycopg2 and potentially other packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Packages required to build psycopg2:
    gcc \
    pkg-config \
    libpq-dev \
    # Clean up to keep image size down
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Overwrite the compiled CSS from the builder stage
COPY --from=tailwind /build/src/static/css/tailwind.css /app/src/static/css/tailwind.css

# Expose the port the app runs on
EXPOSE 8000

# The command to run the app is specified in docker-compose.yml
