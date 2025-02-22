# Используем официальный образ Python
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    binutils \
    libproj-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Отключаем создание байткода и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем переменные окружения для GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

# Проверяем версию GDAL
RUN gdal-config --version

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости по отдельности
COPY requirements.txt .
RUN pip install --no-cache-dir pip setuptools wheel
RUN pip install --no-cache-dir GDAL==3.6.2
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем директории для статики и медиа
RUN mkdir -p /app/static /app/media /app/staticfiles

# Собираем статические файлы
RUN python manage.py collectstatic --noinput || true

# Создаем пользователя
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Проверяем конфигурацию Django
RUN python manage.py check --deploy || true

# Открываем порт
EXPOSE 8001

# Запускаем через gunicorn с правильными настройками
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "drillflow.wsgi:application"] 