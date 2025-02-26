#!/bin/bash

# Скрипт для сборки проекта на Vercel

echo "Начало сборки проекта DrillFlow на Vercel"
echo "Текущая директория: $(pwd)"

# Установка Python зависимостей
echo "Установка Python зависимостей..."
pip install -r requirements-vercel.txt

# Создание директории для статических файлов, если она не существует
if [ ! -d "public" ]; then
  echo "Создание директории public..."
  mkdir -p public
fi

# Копирование статических файлов
echo "Копирование статических файлов..."
cp -r static/* public/ 2>/dev/null || echo "Директория static не найдена или пуста"

# Проверка наличия файла style.css в public
if [ ! -f "public/style.css" ]; then
  echo "Копирование style.css в public..."
  cp public/style.css public/ 2>/dev/null || echo "Файл style.css не найден"
fi

# Проверка наличия favicon.ico
if [ ! -f "public/favicon.ico" ]; then
  echo "Создание базового favicon.ico..."
  touch public/favicon.ico
fi

# Установка Node.js зависимостей
echo "Установка Node.js зависимостей..."
npm install

# Сборка Tailwind CSS
echo "Сборка Tailwind CSS..."
npx tailwindcss -i ./public/style.css -o ./public/style.css --minify

# Создание директории для API
if [ ! -d "api/python" ]; then
  echo "Создание директории api/python..."
  mkdir -p api/python
fi

# Проверка наличия файла index.js в api/python
if [ ! -f "api/python/index.js" ]; then
  echo "ОШИБКА: Файл api/python/index.js не найден!"
  exit 1
fi

# Проверка наличия файла bot.py
if [ ! -f "bot/bot.py" ]; then
  echo "ОШИБКА: Файл bot/bot.py не найден!"
  exit 1
fi

# Проверка наличия файла process_update.py
if [ ! -f "bot/process_update.py" ]; then
  echo "ОШИБКА: Файл bot/process_update.py не найден!"
  exit 1
fi

echo "Сборка завершена успешно!"
exit 0 