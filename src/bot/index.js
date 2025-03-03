const TelegramBot = require('node-telegram-bot-api');
const { PrismaClient } = require('@prisma/client');
const { handleProfile } = require('./handlers/profile');
const { handleOrders } = require('./handlers/orders');
const { handleLocation } = require('./handlers/location');
const { handleDocuments } = require('./handlers/documents');
const { handleSettings } = require('./handlers/settings');
const { handleStart, handleHelp } = require('./handlers');

// Инициализация Prisma
const prisma = new PrismaClient();

function initBot() {
  const bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, {
    polling: process.env.USE_POLLING === '1'
  });

  // Обработчики команд
  bot.onText(/\/start/, (msg) => handleStart(bot, msg));
  bot.onText(/\/help/, (msg) => handleHelp(bot, msg));
  bot.onText(/\/location/, (msg) => handleLocation(bot, msg));

  // Обработка местоположения
  bot.on('location', (msg) => handleLocation(bot, msg));

  // Обработка текстовых сообщений
  bot.on('message', (msg) => {
    if (msg.text && !msg.text.startsWith('/')) {
      const chatId = msg.chat.id;
      switch (msg.text) {
        case '📋 Профиль':
          bot.sendMessage(chatId, 'Функция профиля в разработке');
          break;
        case '📍 Местоположение':
          handleLocation(bot, msg);
          break;
        case '📦 Заказы':
          bot.sendMessage(chatId, 'Функция заказов в разработке');
          break;
        case '⚙️ Настройки':
          bot.sendMessage(chatId, 'Функция настроек в разработке');
          break;
        case '❓ Помощь':
          handleHelp(bot, msg);
          break;
        case '🔙 Назад':
          handleStart(bot, msg);
          break;
      }
    }
  });

  // Обработка callback запросов
  bot.on('callback_query', (query) => {
    const chatId = query.message.chat.id;
    bot.answerCallbackQuery(query.id);
    bot.sendMessage(chatId, 'Функция в разработке');
  });

  // Обработка ошибок
  bot.on('error', (error) => {
    console.error('Ошибка в боте:', error);
  });

  bot.on('polling_error', (error) => {
    console.error('Ошибка при поллинге:', error);
  });

  return bot;
}

// Обработка callback запросов
bot.on('callback_query', async (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;

  try {
    switch (data) {
      case 'profile':
        await handleProfile(bot, query, prisma);
        break;
      case 'create_order':
      case 'my_orders':
        await handleOrders(bot, query, prisma);
        break;
      case 'settings':
        await handleSettings(bot, query, prisma);
        break;
      case 'help':
        await sendHelp(bot, chatId);
        break;
      default:
        if (data.startsWith('order_')) {
          await handleOrders(bot, query, prisma);
        } else if (data.startsWith('profile_')) {
          await handleProfile(bot, query, prisma);
        } else if (data.startsWith('settings_')) {
          await handleSettings(bot, query, prisma);
        }
    }

    // Отвечаем на callback запрос
    await bot.answerCallbackQuery(query.id);
  } catch (error) {
    console.error('Ошибка при обработке callback:', error);
    await bot.sendMessage(chatId, 'Произошла ошибка. Пожалуйста, попробуйте позже.');
  }
});

// Обработка фото и документов
bot.on('photo', async (msg) => {
  try {
    await handleDocuments(bot, msg, prisma, 'photo');
  } catch (error) {
    console.error('Ошибка при обработке фото:', error);
    await bot.sendMessage(msg.chat.id, 'Произошла ошибка при обработке фото.');
  }
});

bot.on('document', async (msg) => {
  try {
    await handleDocuments(bot, msg, prisma, 'document');
  } catch (error) {
    console.error('Ошибка при обработке документа:', error);
    await bot.sendMessage(msg.chat.id, 'Произошла ошибка при обработке документа.');
  }
});

// Функция отправки справки
async function sendHelp(bot, chatId) {
  const helpText = `🔍 Как пользоваться ботом:

📝 Создание заказа:
1. Нажмите "Создать заказ"
2. Выберите тип услуги
3. Укажите адрес
4. Добавьте описание
5. При желании прикрепите фото
6. Подтвердите создание заказа

🔍 Просмотр заказов:
- "Мои заказы" покажет все ваши заказы
- Используйте фильтры для поиска
- Нажмите на заказ для подробностей

👤 Профиль:
- Укажите контактные данные
- Загрузите необходимые документы
- Настройте радиус поиска (для подрядчиков)

⚙️ Настройки:
- Управляйте уведомлениями
- Настройте звук
- Измените язык

❓ Нужна помощь?
Напишите в поддержку: @support`;

  await bot.sendMessage(chatId, helpText, {
    parse_mode: 'Markdown'
  });
}

// Экспорт бота и Prisma клиента
module.exports = {
  initBot,
  prisma
}; 