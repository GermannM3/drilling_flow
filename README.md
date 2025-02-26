# DrillFlow - Платформа для распределения заказов на бурение

## Архитектура

Проект построен на основе следующих компонентов:

1. **Telegram Bot** (Основной интерфейс)
   - Обработка команд пользователей
   - Управление заказами
   - Система рейтингов
   - Интеграция с платежами

2. **FastAPI Backend**
   - REST API для админ-панели
   - Обработка webhook'ов от Telegram
   - Интеграция с внешними сервисами

3. **Nginx**
   - Reverse proxy
   - Статические файлы
   - SSL/TLS
   - Кэширование

## Мониторинг и поддержка

### Проверка здоровья
- `/health` - общий статус
- `/bot-health` - статус Telegram бота
- Логи в `/app/logs/`

### Метрики
- Prometheus метрики
- Grafana дашборды
- Алерты через Telegram

## Развертывание

Проект автоматически развертывается на Timeweb Cloud:
1. Push в main ветку
2. Автоматическая сборка Docker образа
3. Деплой на germannm3-drilling-flow-12c3.twc1.net

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

## Лицензии и правовая информация

### Яндекс Карты
Приложение использует сервисы Яндекс Карт на условиях [лицензионного соглашения](https://yandex.ru/legal/maps_api/).

При использовании карт необходимо:
- Размещать ссылку на условия использования
- Показывать копирайт "© Яндекс Карты"
- Не превышать лимиты бесплатного использования

## Развертывание

### Рабочие окружения

Продакшен: https://germannm3-drilling-flow-12c3.twc1.net
IP: 92.255.110.28

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

## Telegram Bot

Бот является основным интерфейсом взаимодействия с пользователями. Он обеспечивает:

### Для клиентов:
- Оформление заказов на бурение
- Отслеживание статуса заказа
- Связь с подрядчиком
- Оплату услуг
- Оставление отзывов

### Для подрядчиков:
- Регистрацию и верификацию
- Получение заказов
- Управление профилем
- Просмотр рейтинга
- Получение оплаты

### Команды бота:
- /start - Начало работы
- /help - Справка
- /profile - Профиль пользователя
- /order - Создать заказ
- /status - Статус текущих заказов
- /support - Связь с поддержкой

### Мониторинг:
- Автоматическая проверка здоровья бота
- Логирование всех действий
- Уведомления администраторов о проблемах
- Метрики производительности

### Развертывание:
1. Убедитесь, что установлен токен бота в .env:
   ```
   TELEGRAM_TOKEN=your_bot_token
   ```
2. Бот автоматически запускается при деплое
3. Проверить статус можно по адресу:
   ```
   https://germannm3-drilling-flow-12c3.twc1.net/bot-health
   ``` 

# DrillFlow Bot

Телеграм-бот для автоматизации распределения заказов на буровые работы. Построен с использованием FastAPI и aiogram 3.x.

## Технологический стек

- Python 3.11
- FastAPI
- aiogram 3.x
- PostgreSQL
- Alembic (миграции)
- Vercel (деплой)

## Структура проекта

```
drilling_flow/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── webhook.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bot.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── migrations/
│   └── vercel.py
├── public/
│   ├── style.css
│   └── index.html
├── alembic.ini
├── requirements.txt
├── vercel.json
├── vercel.sh
└── README.md
```

## Локальная разработка

### Предварительные требования

- Python 3.11+
- pip
- PostgreSQL
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/drilling_flow.git
cd drilling_flow
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\\Scripts\\activate   # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории:
```env
TELEGRAM_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:password@localhost:5432/drilling_flow
TELEGRAM_BOT_DOMAIN=your_domain
USE_POLLING=True  # для локальной разработки
```

### Запуск

1. Запустите PostgreSQL

2. Примените миграции:
```bash
alembic upgrade head
```

3. Запустите бот в режиме разработки:
```bash
python -m app.core.bot
```

## Деплой на Vercel

### Предварительные требования

- Аккаунт на Vercel
- Установленный Vercel CLI
- Домен (опционально)

### Шаги деплоя

1. Установите Vercel CLI:
```bash
npm i -g vercel
```

2. Войдите в свой аккаунт:
```bash
vercel login
```

3. Настройте переменные окружения на Vercel:
- TELEGRAM_TOKEN
- DATABASE_URL
- TELEGRAM_BOT_DOMAIN
- USE_POLLING=False

4. Выполните деплой:
```bash
vercel --prod
```

5. Настройте вебхук для бота:
```bash
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=https://your-domain.vercel.app/api/webhook"
```

### Проверка работы

1. Откройте URL вашего бота в Telegram
2. Проверьте статус вебхука:
```bash
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"
```

## Мониторинг и логи

- Логи доступны в панели управления Vercel
- Для локальной разработки логи выводятся в консоль
- Формат логов: `[timestamp] level name - message`

## Безопасность

- Все запросы к API защищены CORS
- Используется HTTPS
- Проверка Telegram токена
- Валидация входящих данных

## Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь, что все переменные окружения установлены
3. Проверьте статус вебхука
4. Создайте issue в репозитории

## Лицензия

MIT 