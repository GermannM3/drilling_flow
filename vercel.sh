#!/bin/bash

# Exit on any error
set -e

# Function for logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function for error handling
handle_error() {
    log "Error occurred in script at line $1"
    exit 1
}

# Set up error handling
trap 'handle_error $LINENO' ERR

# Setup environment
log "Setting up environment variables..."

# Core settings
export VERCEL=1
export USE_POLLING=False
export PYTHONPATH=.

# Webhook configuration
export TELEGRAM_BOT_DOMAIN="drilling-flow.vercel.app"
export BOT_WEBHOOK_URL="https://drilling-flow.vercel.app/api/webhook"

# Verify required environment variables
log "Verifying environment variables..."
required_vars=("TELEGRAM_TOKEN" "TELEGRAM_BOT_DOMAIN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log "Error: $var is not set"
        exit 1
    fi
done

# Install dependencies
log "Installing dependencies..."
if ! pip install -r requirements.txt; then
    log "Error: Failed to install dependencies"
    exit 1
fi

# Verify configuration
log "Verifying application configuration..."
if ! python -c "from app.core.config import get_settings; print('Configuration loaded successfully')"; then
    log "Error: Failed to load application configuration"
    exit 1
fi

# Start application
log "Starting application..."
exec "$@"

log "Setup completed successfully" 