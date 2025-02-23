#!/bin/bash

# Основные директории приложения
mkdir -p app/{api,bot,core,db,models,schemas,services}
mkdir -p tests/{api,bot,db,services}

# Создание __init__.py файлов
touch app/__init__.py
touch app/api/__init__.py
touch app/bot/__init__.py
touch app/core/__init__.py
touch app/db/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py

touch tests/__init__.py
touch tests/api/__init__.py
touch tests/bot/__init__.py
touch tests/db/__init__.py
touch tests/services/__init__.py 