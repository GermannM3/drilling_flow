# DrillFlow - Документация

## Содержание
1. [Обзор проекта](#обзор-проекта)
2. [Архитектура](#архитектура)
3. [Компоненты](#компоненты)
4. [Установка и запуск](#установка-и-запуск)
5. [API](#api)
6. [Telegram Bot](#telegram-bot)
7. [Мониторинг](#мониторинг)
8. [FAQ](#faq)

## Обзор проекта

DrillFlow - это автоматизированная платформа для распределения заказов на бурение между подрядчиками. Система использует геолокацию, рейтинги и текущую загрузку для оптимального распределения заказов.

### Ключевые возможности
- Автоматическое распределение заказов
- Рейтинговая система подрядчиков
- Интеграция с платежными системами
- Геолокационный поиск исполнителей
- Система отзывов и оценок

## Архитектура

### Основные компоненты
```
DrillFlow/
├── app/                    # Основной код приложения
│   ├── api/               # REST API endpoints
│   ├── bot/               # Telegram бот
│   ├── core/              # Базовая конфигурация
│   ├── db/                # Работа с базой данных
│   └── services/          # Бизнес-логика
├── docker/                # Docker конфигурации
│   ├── nginx/            # Настройки Nginx
│   └── supervisor/       # Настройки Supervisor
└── tests/                # Тесты
```

## Компоненты

### Telegram Bot
Основной интерфейс взаимодействия с пользователями.

#### Команды бота
- `/start` - Начало работы
- `/help` - Справка
- `/profile` - Профиль пользователя
- `/order` - Создать заказ
- `/status` - Статус заказов
- `/support` - Поддержка

#### Роли пользователей
1. **Клиенты**
   - Создание заказов
   - Отслеживание статуса
   - Оплата услуг
   - Оставление отзывов

2. **Подрядчики**
   - Регистрация и верификация
   - Прием заказов
   - Управление профилем
   - Просмотр рейтинга

### API Endpoints

#### Публичные endpoints
```
GET /health           # Проверка здоровья сервиса
GET /bot/health      # Проверка состояния бота
POST /webhook        # Webhook для Telegram
```

#### Защищенные endpoints
```
GET /api/orders      # Список заказов
POST /api/orders    # Создание заказа
GET /api/profile    # Профиль пользователя
```

## Установка и запуск

### Требования
- Docker
- Docker Compose
- PostgreSQL
- Redis

### Переменные окружения
```env
# Основные настройки
HOST=0.0.0.0
PORT=8080
WORKERS=4

# База данных
POSTGRES_SERVER=db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=drillflow

# Telegram
TELEGRAM_TOKEN=your_bot_token
BOT_WEBHOOK_URL=https://your-domain.com/webhook
```

### Запуск
1. Клонируйте репозиторий
2. Создайте `.env` файл
3. Запустите через Docker:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Мониторинг

### Логи
- `/app/logs/telegram_bot.log` - Логи бота
- `/app/logs/uvicorn.log` - Логи API
- `/app/logs/nginx.log` - Логи Nginx

### Метрики
- `/metrics` - Prometheus метрики
- Grafana дашборды для визуализации

### Проверка здоровья
- `/health` - Общий статус
- `/bot-health` - Статус бота

## FAQ

### Общие вопросы

**Q: Как изменить количество воркеров?**
A: Установите переменную окружения `WORKERS`. Рекомендуется: CPU * 2 + 1

**Q: Как обновить SSL сертификат?**
A: Сертификаты управляются автоматически через Timeweb Cloud

**Q: Где находятся логи?**
A: Все логи в директории `/app/logs/`

### Разработка

**Q: Как добавить новую команду боту?**
A: Создайте новый handler в `app/bot/handlers/` и зарегистрируйте в `app/bot/main.py`

**Q: Как изменить настройки Nginx?**
A: Конфигурации находятся в `docker/nginx/conf.d/`

### Деплой

**Q: Как обновить приложение?**
A: Push в main ветку автоматически запустит деплой

**Q: Как откатить изменения?**
A: Используйте revert в git и сделайте push

## Безопасность

### Основные меры
- Rate limiting
- SSL/TLS
- Проверка токенов
- Валидация входных данных

### Рекомендации
1. Регулярно обновляйте зависимости
2. Мониторьте логи
3. Используйте strong passwords
4. Проверяйте права доступа

## Поддержка

### Контакты
- Telegram: @support_group
- Email: support@example.com

### Сообщение об ошибках
1. Проверьте логи
2. Опишите проблему
3. Приложите примеры
4. Отправьте в поддержку 