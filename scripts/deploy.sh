#!/bin/bash

set -e

echo "Pulling latest changes..."
git pull

echo "Building containers..."
docker-compose build

echo "Starting core services..."
docker-compose up -d db redis

echo "Waiting for database..."
sleep 10

echo "Running migrations..."
docker-compose run --rm api alembic upgrade head

echo "Starting API and bot..."
docker-compose up -d api bot celery nginx certbot

echo "Waiting for API..."
sleep 10

echo "Starting monitoring..."
docker-compose up -d prometheus grafana

echo "Checking services health..."
docker-compose ps

echo "Deployment completed!" 