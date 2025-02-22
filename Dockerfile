# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаем пользователя
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Проверяем конфигурацию Django
RUN python manage.py check --deploy || true

# Открываем порт
EXPOSE 8001

# Запускаем через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"] 