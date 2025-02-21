# DrillFlow

DrillFlow — автоматизированная платформа для распределения заказов на бурение между подрядчиками на основе геолокации, рейтинга и загрузки.

## Основные возможности

### Telegram-бот
- Регистрация и верификация подрядчиков
  - Проверка документов
  - Модерация профилей
  - Защита от мультиаккаунтинга
- Управление профилем подрядчика
  - Настройка радиуса работы (до 100 км)
  - Установка максимальной загрузки
  - Управление уведомлениями
- Система распределения заказов
  - Автоматический подбор по геолокации
  - Приоритезация по рейтингу
  - Таймер подтверждения (5 минут)
- Рейтинговая система
  - Начисление баллов за выполнение
  - Штрафы за нарушения
  - Влияние на приоритет заказов

### Клиентский интерфейс
- Оформление заказов
  - Выбор типа услуг
  - Геолокация
  - Загрузка фото/описания
- Отслеживание статуса
- Система оплаты
  - Предоплата 20%
  - Возврат средств
- Отзывы и оценки

### Админ-панель
- Управление пользователями
  - Верификация подрядчиков
  - Блокировка нарушителей
  - Корректировка рейтингов
- Мониторинг заказов
  - Ручное распределение
  - Обработка конфликтов
- Аналитика и отчетность
  - Статистика и графики
  - Экспорт данных

## Технический стек

### Бэкенд
- Python 3.11+
- Django 4.2+
- Django REST Framework
- Celery для асинхронных задач
- Redis для кэширования

### Безопасность
- SSL/TLS шифрование
- DDoS-защита
- Антифрод система
- Резервное копирование

### Интеграции
- Telegram Bot API
- Google Maps Geocoding API
- Платежные системы:
  - Система быстрых платежей (СБП)
  - YooMoney
  - Stripe
- Антифрод: ip-api.com

## Установка и запуск

### Через Docker
```bash
# Клонирование репозитория
git clone https://github.com/GermannM3/drilling_flow.git
cd drilling_flow

# Запуск через Docker Compose
docker-compose up -d
```

### Локальная установка
```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл

# Миграции и запуск
python manage.py migrate
python manage.py runserver
```

## Документация
- [Руководство разработчика](docs/developer-guide.md)
- [API документация](docs/api.md)
- [Архитектура проекта](docs/architecture.md)

## Лицензия
MIT License 

# DrillFlow API

FastAPI приложение для управления буровыми работами.

## Развертывание

### Требования
- Docker
- PostgreSQL
- Redis

### Переменные окружения
Создайте файл `.env` со следующими переменными:

```env
# База данных
POSTGRES_DB=drillflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://postgres:your_password@db:5432/drillflow

# Redis
REDIS_URL=redis://redis:6379/0

# Безопасность
SECRET_KEY=your_secret_key
ALGORITHM=HS256

# API ключи
GOOGLE_MAPS_API_KEY=your_google_maps_key
TELEGRAM_BOT_TOKEN=your_bot_token
```

### Запуск
```bash
# Сборка
docker build -t drilling-flow -f Dockerfile.prod .

# Запуск
docker run -d -p 8001:8001 --env-file .env drilling-flow
``` 