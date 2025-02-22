FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Сканирование уязвимостей
FROM aquasec/trivy:latest as trivy
COPY --from=builder /app /app
RUN trivy filesystem --no-progress --exit-code 1 --severity HIGH,CRITICAL /app

# Финальный образ
FROM python:3.11-slim

# Установка системных зависимостей от root
USER root
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Настройки безопасности
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir --user /wheels/*

# Копирование кода приложения
COPY --chown=appuser:appuser . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"] 