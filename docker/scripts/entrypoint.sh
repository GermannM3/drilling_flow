#!/bin/bash
set -e

# Настройка системных лимитов
ulimit -n 65535
echo never > /sys/kernel/mm/transparent_hugepage/enabled

# Применение миграций БД
alembic upgrade head

# Настройка SSL если указан домен
if [ ! -z "$DOMAIN" ]; then
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $ADMIN_EMAIL
fi

# Запуск supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 