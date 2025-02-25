#!/bin/bash

# Выводим версии Python и pip
echo "Python version:"
python3 --version || python --version
echo "Pip version:"
python3 -m pip --version || python -m pip --version

# Устанавливаем зависимости для Vercel
python3 -m pip install -r requirements-vercel.txt || python -m pip install -r requirements-vercel.txt

# Создаем директории для статических файлов
mkdir -p app/static/webapp/images
mkdir -p app/templates

# Создаем директорию public для Vercel
mkdir -p public

# Копируем статические файлы
cp -r static/* app/static/ || true
cp -r app/static/* public/ || true

echo "Build completed successfully!" 