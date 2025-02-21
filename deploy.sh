#!/bin/bash

echo "Pulling latest changes..."
git pull

echo "Building containers..."
docker-compose -f docker-compose.prod.yml build

echo "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --no-input

echo "Applying migrations..."
docker-compose exec -T web python manage.py migrate

echo "Restarting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "Deployment completed!" 