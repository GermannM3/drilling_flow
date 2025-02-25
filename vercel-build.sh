#!/bin/bash

# Устанавливаем зависимости для Vercel
pip install -r requirements-vercel.txt

# Создаем директории для статических файлов
mkdir -p app/static/webapp/images
mkdir -p app/templates

# Копируем статические файлы
cp -r static/* app/static/ || true

echo "Build completed successfully!" 