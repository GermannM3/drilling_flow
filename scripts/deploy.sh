#!/bin/bash

set -e

echo "Pulling latest changes..."
git pull

echo "Building containers..."
docker-compose build

echo "Starting services..."
docker-compose up -d db redis

echo "Waiting for database..."
sleep 10

echo "Running migrations..."
docker-compose run --rm api alembic upgrade head

echo "Collecting static files..."
docker-compose run --rm api python manage.py collectstatic --noinput

echo "Starting all services..."
docker-compose up -d

echo "Checking services health..."
docker-compose ps

echo "Deployment completed!" 