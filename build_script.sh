#!/bin/bash

# Exit on error
set -e

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Install dependencies
log "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
log "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput

log "Build completed successfully."
