#!/bin/bash

# Создаем директории для certbot
mkdir -p certbot/conf
mkdir -p certbot/www

# Запускаем nginx для проверки домена
docker-compose up -d nginx

# Ждем запуска nginx
sleep 5

# Получаем SSL сертификат
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email your@email.com \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d germannm3-drilling-flow-842b.twc1.net 