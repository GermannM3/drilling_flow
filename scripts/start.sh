#!/bin/bash

# Остановить все контейнеры
docker-compose down

# Удалить все контейнеры и образы
docker system prune -af

# Собрать и запустить
docker-compose up --build -d

# Применить миграции
docker-compose exec api alembic upgrade head

# Показать логи
docker-compose logs -f 