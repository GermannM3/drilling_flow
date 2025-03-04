/**
 * @fileoverview Обработчик подписок для Telegram бота
 */

const { 
  getUserByTelegramId,
  updateUser 
} = require('../../utils/database');
const { handleTelegramError } = require('../../utils/errorHandler');
const { 
  getMainMenuKeyboard,
  getSubscriptionKeyboard 
} = require('../../utils/keyboards');
const { formatSubscriptionInfo } = require('../../utils/messages');
const config = require('../../config/default');

/**
 * Обработчик команды "🔄 Подписка"
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} msg - Сообщение пользователя
 */
const handleSubscription = async (bot, msg) => {
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
    handleTelegramError(error, { method: 'handleSubscription', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при загрузке информации о подписке. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Обработчик callback-запросов для подписок
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} query - Callback query
 */
const handleSubscriptionCallback = async (bot, query) => {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;
  
  try {
    await bot.answerCallbackQuery(query.id);
    
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
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
      
      await bot.sendMessage(chatId, `<b>✅ Подписка продлена!</b>

Ваша подписка "${user.subscription.plan}" активна до ${expDate.toLocaleDateString('ru-RU')}`, {
        parse_mode: 'HTML',
        reply_markup: getMainMenuKeyboard()
      });
    }
    else if (data === 'subscription_cancel') {
      await updateUser(userId, {
        subscription: {
          ...user.subscription,
          status: 'INACTIVE'
        }
      });
      
      await bot.sendMessage(chatId, `<b>❌ Подписка отменена</b>

Ваша подписка будет действовать до конца оплаченного периода, а затем автоматически отключится.`, {
        parse_mode: 'HTML',
        reply_markup: getMainMenuKeyboard()
      });
    }
    else if (data.startsWith('subscription_')) {
      const plan = data.replace('subscription_', '');
      const { subscriptionPlans } = config.payments;
      const planData = subscriptionPlans[plan.toLowerCase()];
      
      if (!planData) {
        throw new Error('Неверный тип подписки');
      }
      
      // Перенаправляем на оплату
      const { handleSubscriptionPayment } = require('./payments');
      await handleSubscriptionPayment(bot, query.message, plan);
    }
  } catch (error) {
    handleTelegramError(error, { method: 'handleSubscriptionCallback', userId, data });
    await bot.sendMessage(chatId, 'Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Проверяет и обновляет статусы подписок
 * @param {TelegramBot} bot - Экземпляр бота
 */
const checkSubscriptions = async (bot) => {
  try {
    const now = new Date();
    
    // Получаем всех пользователей с активными подписками
    const users = await prisma.user.findMany({
      where: {
        subscription: {
          status: 'ACTIVE'
        }
      },
      include: {
        subscription: true
      }
    });
    
    for (const user of users) {
      const expDate = new Date(user.subscription.expirationDate.split('.').reverse().join('-'));
      
      // Если подписка истекла
      if (expDate <= now) {
        if (user.subscription.autoRenew) {
          // Здесь должна быть логика автопродления
          // В данном примере просто уведомляем пользователя
          await bot.sendMessage(user.telegramId, `<b>⚠️ Внимание!</b>

Срок действия вашей подписки "${user.subscription.plan}" истек.
Автопродление временно недоступно. Пожалуйста, продлите подписку вручную.`, {
            parse_mode: 'HTML'
          });
        }
        
        // Отключаем подписку
        await updateUser(user.telegramId, {
          subscription: {
            ...user.subscription,
            status: 'INACTIVE'
          }
        });
        
        await bot.sendMessage(user.telegramId, `<b>❌ Подписка отключена</b>

Срок действия вашей подписки "${user.subscription.plan}" истек.
Для продолжения использования всех возможностей бота, пожалуйста, оформите новую подписку.`, {
          parse_mode: 'HTML'
        });
      }
      // Если до истечения осталось 3 дня или меньше
      else if ((expDate - now) / (1000 * 60 * 60 * 24) <= 3) {
        await bot.sendMessage(user.telegramId, `<b>⚠️ Внимание!</b>

Срок действия вашей подписки "${user.subscription.plan}" истекает ${user.subscription.expirationDate}.
${user.subscription.autoRenew ? 'Подписка будет продлена автоматически.' : 'Не забудьте продлить подписку!'}`, {
          parse_mode: 'HTML'
        });
      }
    }
  } catch (error) {
    handleTelegramError(error, { method: 'checkSubscriptions' });
  }
};

module.exports = {
  handleSubscription,
  handleSubscriptionCallback,
  checkSubscriptions
}; 