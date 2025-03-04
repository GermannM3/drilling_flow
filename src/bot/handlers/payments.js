/**
 * @fileoverview Обработчик платежей для Telegram бота
 */

const { 
  getUserByTelegramId,
  updateUser 
} = require('../../utils/database');
const { handleTelegramError } = require('../../utils/errorHandler');
const { 
  getMainMenuKeyboard,
  getTestPaymentKeyboard,
  createInlineKeyboard 
} = require('../../utils/keyboards');
const { formatCurrency } = require('../../utils/common');
const config = require('../../config/default');

/**
 * Обработчик команды "💳 Тестовый платеж"
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} msg - Сообщение пользователя
 */
const handleTestPayment = async (bot, msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    await bot.sendMessage(chatId, `<b>💳 Тестовый платеж</b>

Вы можете протестировать систему платежей на примере тестового платежа.

<b>Сумма:</b> 100 ₽
<b>Назначение:</b> Тестирование системы оплаты
<b>Метод:</b> Банковская карта

<i>Это тестовый платеж, реальные деньги не будут списаны</i>`, {
      parse_mode: 'HTML',
      reply_markup: getTestPaymentKeyboard()
    });
  } catch (error) {
    handleTelegramError(error, { method: 'handleTestPayment', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при обработке платежа. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Обработчик платежа по подписке
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} msg - Сообщение пользователя
 * @param {string} plan - Тип подписки
 */
const handleSubscriptionPayment = async (bot, msg, plan) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    const { subscriptionPlans } = config.payments;
    const planData = subscriptionPlans[plan.toLowerCase()];
    
    if (!planData) {
      throw new Error('Неверный тип подписки');
    }
    
    const keyboard = createInlineKeyboard([
      [{ text: `💳 Оплатить ${formatCurrency(planData.price)}`, callback_data: `pay_subscription_${plan}` }],
      [{ text: "🔙 Назад", callback_data: "back_to_subscription" }]
    ]);
    
    await bot.sendMessage(chatId, `<b>💳 Оплата подписки "${planData.name}"</b>

<b>Стоимость:</b> ${formatCurrency(planData.price)}
<b>Период:</b> 1 месяц

<b>Включено в тариф:</b>
${planData.features.map(feature => `• ${feature}`).join('\n')}

<i>Нажмите кнопку "Оплатить" для перехода к оплате</i>`, {
      parse_mode: 'HTML',
      reply_markup: keyboard
    });
  } catch (error) {
    handleTelegramError(error, { method: 'handleSubscriptionPayment', userId, plan });
    await bot.sendMessage(chatId, 'Произошла ошибка при обработке платежа. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Обработчик вывода средств
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} msg - Сообщение пользователя
 * @param {string} method - Метод вывода
 */
const handleWithdraw = async (bot, msg, method) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    if (user.finance.currentBalance <= 0) {
      await bot.sendMessage(chatId, `<b>❌ Недостаточно средств</b>

На вашем балансе нет доступных средств для вывода.`, {
        parse_mode: 'HTML',
        reply_markup: getMainMenuKeyboard()
      });
      return;
    }
    
    const amount = user.finance.currentBalance;
    const withdrawalId = 'W-' + Date.now().toString().slice(-8);
    
    // Обновляем баланс пользователя
    await updateUser(userId, {
      finance: {
        ...user.finance,
        currentBalance: 0,
        pendingBalance: user.finance.pendingBalance + amount
      }
    });
    
    let methodName = '';
    switch (method) {
      case 'card':
        methodName = 'банковскую карту';
        break;
      case 'sbp':
        methodName = 'СБП';
        break;
      case 'wallet':
        methodName = 'электронный кошелек';
        break;
    }
    
    await bot.sendMessage(chatId, `<b>✅ Запрос на вывод средств принят</b>

<b>Сумма:</b> ${formatCurrency(amount)}
<b>Метод:</b> ${methodName}
<b>ID транзакции:</b> ${withdrawalId}

Средства поступят на ваш счет в течение 24 часов. Статус транзакции можно отслеживать в разделе "Доход".`, {
      parse_mode: 'HTML',
      reply_markup: getMainMenuKeyboard()
    });
  } catch (error) {
    handleTelegramError(error, { method: 'handleWithdraw', userId, withdrawMethod: method });
    await bot.sendMessage(chatId, 'Произошла ошибка при обработке вывода средств. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Обработчик callback-запросов для платежей
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} query - Callback query
 */
const handlePaymentCallback = async (bot, query) => {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;
  
  try {
    await bot.answerCallbackQuery(query.id);
    
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    if (data.startsWith('pay_test_')) {
      const amount = parseInt(data.replace('pay_test_', ''));
      await bot.sendMessage(chatId, `<b>✅ Тестовый платеж на сумму ${formatCurrency(amount)} успешно выполнен</b>

Спасибо за тестирование системы оплаты!

Номер транзакции: TX-${Date.now().toString().slice(-8)}`, {
        parse_mode: 'HTML',
        reply_markup: getMainMenuKeyboard()
      });
    }
    else if (data.startsWith('pay_subscription_')) {
      const plan = data.replace('pay_subscription_', '');
      const { subscriptionPlans } = config.payments;
      const planData = subscriptionPlans[plan.toLowerCase()];
      
      if (!planData) {
        throw new Error('Неверный тип подписки');
      }
      
      // В реальном приложении здесь была бы интеграция с платежным шлюзом
      const now = new Date();
      const expDate = new Date(now);
      expDate.setMonth(expDate.getMonth() + 1);
      
      await updateUser(userId, {
        subscription: {
          status: 'ACTIVE',
          plan: planData.name,
          activationDate: now.toLocaleDateString('ru-RU'),
          expirationDate: expDate.toLocaleDateString('ru-RU'),
          features: planData.features
        }
      });
      
      await bot.sendMessage(chatId, `<b>✅ Подписка успешно оформлена!</b>

<b>Тариф:</b> ${planData.name}
<b>Стоимость:</b> ${formatCurrency(planData.price)}
<b>Период:</b> 1 месяц
<b>Действует до:</b> ${expDate.toLocaleDateString('ru-RU')}

<b>Доступные возможности:</b>
${planData.features.map(feature => `• ${feature}`).join('\n')}`, {
        parse_mode: 'HTML',
        reply_markup: getMainMenuKeyboard()
      });
    }
    else if (data.startsWith('withdraw_')) {
      const method = data.replace('withdraw_', '');
      await handleWithdraw(bot, query.message, method);
    }
  } catch (error) {
    handleTelegramError(error, { method: 'handlePaymentCallback', userId, data });
    await bot.sendMessage(chatId, 'Произошла ошибка при обработке платежа. Пожалуйста, попробуйте позже.');
  }
};

module.exports = {
  handleTestPayment,
  handleSubscriptionPayment,
  handleWithdraw,
  handlePaymentCallback
}; 