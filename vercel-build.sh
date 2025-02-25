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
mkdir -p app/static/webapp/css
mkdir -p app/static/webapp/js
mkdir -p app/templates

# Создаем директорию public для Vercel
mkdir -p public
mkdir -p public/css
mkdir -p public/js
mkdir -p public/images

# Копируем статические файлы
cp -r app/static/webapp/* public/ || true
cp -r app/static/css/* public/css/ || true
cp -r app/static/js/* public/js/ || true

# Создаем пустой файл style.css если его нет
touch public/style.css

echo "Build completed successfully!" 