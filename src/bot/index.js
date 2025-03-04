/**
 * @fileoverview Основной файл Telegram бота DrillFlow
 */

const TelegramBot = require('node-telegram-bot-api');
const config = require('../config/default');
const { handleTelegramError } = require('../utils/errorHandler');
const { 
  getUserByTelegramId, 
  updateUser 
} = require('../utils/database');
const {
  getMainMenuKeyboard,
  getProfileKeyboard,
  getSettingsKeyboard,
  getSubscriptionKeyboard,
  getOrdersKeyboard,
  getStatusKeyboard,
  getTestPaymentKeyboard
} = require('../utils/keyboards');
const {
  formatUserProfile,
  formatOrdersList,
  formatUserStats,
  formatSubscriptionInfo,
  formatIncomeInfo
} = require('../utils/messages');

// Инициализация бота
const bot = new TelegramBot(config.bot.token, {
  polling: process.env.USE_POLLING === '1'
});

// Обработка команды /start
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    let user = await getUserByTelegramId(userId);
    
    if (!user) {
      // Создаем нового пользователя
      const now = new Date();
      user = await updateUser(userId, {
        telegramId: userId,
        name: msg.from.first_name,
        status: 'Активен',
        role: 'CLIENT',
        rating: 5.0,
        registrationDate: now.toLocaleDateString('ru-RU')
      });
    }
    
    const welcomeMessage = `<b>👋 Добро пожаловать в DrillFlow Bot!</b>

Это система управления буровыми работами.

Чем я могу помочь вам сегодня?`;
    
    await bot.sendMessage(chatId, welcomeMessage, {
      parse_mode: 'HTML',
      reply_markup: getMainMenuKeyboard()
    });
  } catch (error) {
    handleTelegramError(error, { method: 'start', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.');
  }
});

// Обработка команды "📋 Профиль"
bot.onText(/📋 Профиль/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    await bot.sendMessage(chatId, formatUserProfile(user), {
      parse_mode: 'HTML',
      reply_markup: getProfileKeyboard(user)
    });
  } catch (error) {
    handleTelegramError(error, { method: 'profile', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при загрузке профиля. Пожалуйста, попробуйте позже.');
  }
});

// Обработка команды "📊 Статистика"
bot.onText(/📊 Статистика/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    await bot.sendMessage(chatId, formatUserStats(user), {
      parse_mode: 'HTML',
      reply_markup: getMainMenuKeyboard()
    });
  } catch (error) {
    handleTelegramError(error, { method: 'stats', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при загрузке статистики. Пожалуйста, попробуйте позже.');
  }
});

// Обработка команды "🔄 Подписка"
bot.onText(/🔄 Подписка/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    await bot.sendMessage(chatId, formatSubscriptionInfo(user), {
      parse_mode: 'HTML',
      reply_markup: getSubscriptionKeyboard(user)
    });
  } catch (error) {
    handleTelegramError(error, { method: 'subscription', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при загрузке информации о подписке. Пожалуйста, попробуйте позже.');
  }
});

// Обработка команды "💰 Доход"
bot.onText(/💰 Доход/, async (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    await bot.sendMessage(chatId, formatIncomeInfo(user), {
      parse_mode: 'HTML',
      reply_markup: getMainMenuKeyboard()
    });
  } catch (error) {
    handleTelegramError(error, { method: 'income', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при загрузке информации о доходе. Пожалуйста, попробуйте позже.');
  }
});

// Обработка callback-запросов
bot.on('callback_query', async (callbackQuery) => {
  const chatId = callbackQuery.message.chat.id;
  const userId = callbackQuery.from.id;
  const data = callbackQuery.data;
  
  try {
    // Отвечаем на callback, чтобы убрать состояние загрузки с кнопки
    await bot.answerCallbackQuery(callbackQuery.id);
    
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    if (data.startsWith('status_')) {
      const statusMap = {
        status_free: 'Свободен',
        status_busy: 'Занят',
        status_break: 'Перерыв',
        status_unavailable: 'Недоступен'
      };
      
      const newStatus = statusMap[data];
      if (newStatus) {
        await updateUser(userId, { status: newStatus });
        await bot.sendMessage(
          chatId,
          `<b>✅ Статус обновлен</b>\n\nВаш текущий статус: <b>${newStatus}</b>`,
          { 
            parse_mode: 'HTML',
            reply_markup: getMainMenuKeyboard()
          }
        );
      }
    }
    else if (data.startsWith('subscription_')) {
      // Обработка действий с подпиской
      if (data === 'subscription_extend') {
        const now = new Date();
        const expDate = new Date(now);
        expDate.setMonth(expDate.getMonth() + 1);
        
        await updateUser(userId, {
          subscription: {
            ...user.subscription,
            expirationDate: expDate.toLocaleDateString('ru-RU')
          }
        });
        
        await bot.sendMessage(
          chatId,
          `<b>✅ Подписка продлена!</b>\n\nВаша подписка "${user.subscription.plan}" активна до ${expDate.toLocaleDateString('ru-RU')}`,
          { 
            parse_mode: 'HTML',
            reply_markup: getMainMenuKeyboard()
          }
        );
      }
    }
    else if (data === 'back_to_main') {
      await bot.sendMessage(
        chatId,
        '<b>🏠 Главное меню</b>\n\nВыберите нужный пункт меню:',
        { 
          parse_mode: 'HTML',
          reply_markup: getMainMenuKeyboard()
        }
      );
    }
  } catch (error) {
    handleTelegramError(error, { method: 'callback_query', userId, data });
    await bot.sendMessage(chatId, 'Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.');
  }
});

// Обработка ошибок
bot.on('polling_error', (error) => {
  handleTelegramError(error, { method: 'polling_error' });
});

// Экспортируем бота
module.exports = bot; 