#!/bin/bash

# Выводим версии Python и pip
echo "Python version:"
python --version
echo "Pip version:"
pip --version

# Устанавливаем зависимости для Vercel
pip install -r requirements-vercel.txt

# Создаем директории для статических файлов
echo "Создание директорий для статических файлов..."
mkdir -p app/static
mkdir -p app/static/webapp
mkdir -p app/static/webapp/images
mkdir -p app/static/webapp/css
mkdir -p app/static/webapp/js
mkdir -p app/templates

# Создаем директорию public для Vercel
echo "Создание директории public для Vercel..."
mkdir -p public
mkdir -p public/css
mkdir -p public/js
mkdir -p public/images

# Создаем пустые файлы для статических ресурсов
echo "Создание пустых файлов для статических ресурсов..."
touch app/static/webapp/style.css
touch public/style.css

# Копируем статические файлы
echo "Копирование статических файлов..."
cp -r app/static/webapp/* public/ || echo "Не удалось скопировать файлы из app/static/webapp"
ls -la app/static/webapp || echo "Директория app/static/webapp не существует или пуста"
ls -la public || echo "Директория public не существует или пуста"

echo "Build completed successfully!" 