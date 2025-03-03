# DrillFlow - Телеграм бот для поиска подрядчиков

## Описание
DrillFlow - это Telegram бот, который помогает клиентам находить подрядчиков для различных работ, основываясь на их местоположении и специализации. Подрядчики могут загружать свои документы, получать заказы и управлять своим профилем.

## Требования
- Node.js v16 или выше
- PostgreSQL 12 или выше
- Telegram Bot Token (получить у @BotFather)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/drilling_flow.git
cd drilling_flow
```

2. Установите зависимости:
```bash
npm install
```

3. Создайте файл `.env` в корневой директории проекта и заполните его следующими данными:
```env
# Настройки базы данных
DATABASE_URL=postgresql://username:password@localhost:5432/drill_flow_db

# Настройки JWT
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_EXPIRES_IN="24h"

# Настройки Telegram бота
TELEGRAM_BOT_TOKEN=your-bot-token-here

# Настройки сервера
PORT=3001
NODE_ENV=development

# Настройки геолокации
DEFAULT_WORK_RADIUS=10
MAX_WORK_RADIUS=100
```

4. Создайте базу данных PostgreSQL:
```bash
createdb drill_flow_db
```

5. Примените миграции базы данных:
```bash
npx prisma migrate dev
```

## Запуск

1. Запустите бота в режиме разработки:
```bash
npm run dev
```

2. Для production запуска:
```bash
npm run build
npm start
```

## Структура проекта
```
drilling_flow/
├── prisma/
│   └── schema.prisma    # Схема базы данных
├── src/
│   ├── bot/            # Логика Telegram бота
│   │   ├── handlers/   # Обработчики команд
│   │   └── index.js    # Инициализация бота
│   ├── db/             # Работа с базой данных
│   └── index.js        # Точка входа
├── .env                # Переменные окружения
└── package.json        # Зависимости проекта
```

## Основные функции
- Регистрация клиентов и подрядчиков
- Загрузка и верификация документов подрядчиков
- Создание и управление заказами
- Геолокационный поиск подрядчиков
- Система рейтингов и отзывов
- Настройки уведомлений

## Команды бота
- `/start` - Начало работы с ботом
- `/help` - Показать справку
- `/profile` - Управление профилем
- `/settings` - Настройки
- `/location` - Обновить местоположение

## Поддержка
По всем вопросам обращайтесь в группу поддержки: [ссылка на группу]

## Лицензия
MIT License 