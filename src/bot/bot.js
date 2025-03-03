const TelegramBot = require('node-telegram-bot-api');
const { handleStart, handleHelp, handleLocation } = require('./handlers');
const { handleProfile, handleProfileCallback } = require('./handlers/profile');
const { handleOrders, handleOrderAccept, handleOrderCancel, handleOrderComplete } = require('./handlers/orders');
const { handleDocuments, handleDocumentCallback } = require('./handlers/documents');
const { handleSettings, handleSettingsCallback } = require('./handlers/settings');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

function createBot() {
  const bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, {
    polling: process.env.USE_POLLING === '1'
  });

  // Обработчики команд
  bot.onText(/\/start/, (msg) => handleStart(bot, msg));
  bot.onText(/\/help/, (msg) => handleHelp(bot, msg));
  bot.onText(/\/location/, (msg) => handleLocation(bot, msg));
  bot.onText(/\/profile/, (msg) => handleProfile(bot, msg, prisma));
  bot.onText(/\/settings/, (msg) => handleSettings(bot, msg, prisma));

  // Обработка местоположения
  bot.on('location', (msg) => handleLocation(bot, msg));

  // Обработка текстовых сообщений
  bot.on('message', async (msg) => {
    if (msg.text && !msg.text.startsWith('/')) {
      const chatId = msg.chat.id;
      try {
        switch (msg.text) {
          case '📋 Профиль':
            await handleProfile(bot, msg, prisma);
            break;
          case '📍 Местоположение':
            await handleLocation(bot, msg);
            break;
          case '📦 Заказы':
          case '🔍 Поиск заказов':
            await handleOrders(bot, msg, prisma);
            break;
          case '⚙️ Настройки':
            await handleSettings(bot, msg, prisma);
            break;
          case '❓ Помощь':
            await handleHelp(bot, msg);
            break;
          case '🔙 Назад':
            await handleStart(bot, msg);
            break;
          case '🔄 Обновить статус':
          case '💰 Доход':
          case '🔄 Подписка':
          case '💳 Тестовый платеж':
            await handleProfile(bot, msg, prisma, msg.text);
            break;
        }
      } catch (error) {
        console.error('Ошибка при обработке сообщения:', error);
        bot.sendMessage(chatId, 'Произошла ошибка. Пожалуйста, попробуйте позже.');
      }
    }
  });

  // Обработка callback запросов
  bot.on('callback_query', async (query) => {
    const chatId = query.message.chat.id;
    try {
      const data = query.data;

      // Обработка возврата в главное меню
      if (data === 'back_to_menu') {
        await handleStart(bot, query.message);
        await bot.answerCallbackQuery(query.id);
        return;
      }

      // Обработка различных типов callback-запросов
      if (data.startsWith('profile_')) {
        await handleProfileCallback(bot, query, prisma);
      } else if (data.startsWith('order_')) {
        const action = data.split('_')[1];
        switch (action) {
          case 'accept':
            await handleOrderAccept(bot, query, prisma);
            break;
          case 'cancel':
            await handleOrderCancel(bot, query, prisma);
            break;
          case 'complete':
            await handleOrderComplete(bot, query, prisma);
            break;
          default:
            await handleOrders(bot, query, prisma);
        }
      } else if (data.startsWith('settings_')) {
        await handleSettingsCallback(bot, query, prisma);
      } else if (data.startsWith('document_')) {
        await handleDocumentCallback(bot, query, prisma);
      } else {
        switch (data) {
          case 'profile':
            await handleProfile(bot, query.message, prisma);
            break;
          case 'orders':
            await handleOrders(bot, query.message, prisma);
            break;
          case 'settings':
            await handleSettings(bot, query.message, prisma);
            break;
          case 'help':
            await handleHelp(bot, query.message);
            break;
        }
      }

      await bot.answerCallbackQuery(query.id);
    } catch (error) {
      console.error('Ошибка при обработке callback:', error);
      bot.sendMessage(chatId, 'Произошла ошибка. Пожалуйста, попробуйте позже.');
      await bot.answerCallbackQuery(query.id, {
        text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
        show_alert: true
      });
    }
  });

  // Обработка фото и документов
  bot.on('photo', async (msg) => {
    try {
      await handleDocuments(bot, msg, prisma, 'photo');
    } catch (error) {
      console.error('Ошибка при обработке фото:', error);
      bot.sendMessage(msg.chat.id, 'Произошла ошибка при обработке фото.');
    }
  });

  bot.on('document', async (msg) => {
    try {
      await handleDocuments(bot, msg, prisma, 'document');
    } catch (error) {
      console.error('Ошибка при обработке документа:', error);
      bot.sendMessage(msg.chat.id, 'Произошла ошибка при обработке документа.');
    }
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

module.exports = createBot; 