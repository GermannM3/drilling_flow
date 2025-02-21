# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем системные зависимости для GeoDjango (GDAL, GEOS и т.д.)
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Отключаем создание байткода и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости проекта
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем исходный код в контейнер
COPY . /app

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Запускаем приложение, используя Gunicorn
CMD ["gunicorn", "drillflow.wsgi:application", "--bind", "0.0.0.0:8000"] 