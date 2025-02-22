#!/bin/sh
# start.sh - запуск supervisord для управления FastAPI и Telegram-ботом

# Настройка системных лимитов
ulimit -n 65535
echo never > /sys/kernel/mm/transparent_hugepage/enabled

# Установка переменных окружения для оптимизации
export UVICORN_WORKERS=${WORKERS:-4}
export PROMETHEUS_MULTIPROC_DIR=${PROMETHEUS_MULTIPROC_DIR:-/tmp}

# Создание директорий для логов, если их нет
mkdir -p /app/logs

# Запуск supervisord с оптимизированной конфигурацией
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 