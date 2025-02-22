FROM python:3.11-slim as builder

# Установка только необходимых build-time зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Копируем и устанавливаем зависимости отдельно для лучшего кэширования
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser \
    && mkdir -p /app /app/logs /app/static /app/media \
    && chown -R appuser:appuser /app

WORKDIR /app

# Копирование wheel-пакетов и установка зависимостей
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels \
    && rm -rf /root/.cache/pip/*

# Копирование конфигурации и кода
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

# Настройки окружения и оптимизации Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=2 \
    PYTHONHASHSEED=random

# Порт для FastAPI
EXPOSE 8080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 