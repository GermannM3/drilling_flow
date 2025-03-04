/**
 * @fileoverview Обработчик заказов для Telegram бота
 */

const { 
  getUserByTelegramId,
  getActiveOrders,
  createOrder,
  updateOrderStatus
} = require('../../utils/database');
const { handleTelegramError } = require('../../utils/errorHandler');
const { 
  getMainMenuKeyboard,
  getOrdersKeyboard,
  createInlineKeyboard 
} = require('../../utils/keyboards');
const { 
  formatOrderInfo,
  formatOrdersList 
} = require('../../utils/messages');
const { calculateDistance } = require('../../utils/common');
const config = require('../../config/default');

/**
 * Обработчик команды "📦 Заказы"
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} msg - Сообщение пользователя
 */
const handleOrders = async (bot, msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    const orders = await getActiveOrders(userId);
    await bot.sendMessage(chatId, formatOrdersList(orders), {
      parse_mode: 'HTML',
      reply_markup: getOrdersKeyboard(orders)
    });
  } catch (error) {
    handleTelegramError(error, { method: 'handleOrders', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при загрузке заказов. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Обработчик команды "🔍 Поиск заказов"
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} msg - Сообщение пользователя
 */
const handleOrderSearch = async (bot, msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    const keyboard = createInlineKeyboard([
      [
        { text: "📍 По местоположению", callback_data: "search_location" },
        { text: "🔧 По типу работ", callback_data: "search_type" }
      ],
      [
        { text: "💰 По стоимости", callback_data: "search_price" },
        { text: "🕒 По сроку", callback_data: "search_deadline" }
      ],
      [
        { text: "🔄 Показать все заказы", callback_data: "search_all" }
      ],
      [
        { text: "🔙 Назад", callback_data: "back_to_main" }
      ]
    ]);
    
    await bot.sendMessage(chatId, `<b>🔍 Поиск заказов</b>

Выберите параметры поиска заказов:

• По местоположению
• По типу работ
• По стоимости
• По сроку выполнения

<i>Нажмите на соответствующую кнопку для начала поиска</i>`, {
      parse_mode: 'HTML',
      reply_markup: keyboard
    });
  } catch (error) {
    handleTelegramError(error, { method: 'handleOrderSearch', userId });
    await bot.sendMessage(chatId, 'Произошла ошибка при поиске заказов. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Обработчик создания нового заказа
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} msg - Сообщение пользователя
 * @param {Object} orderData - Данные заказа
 */
const handleCreateOrder = async (bot, msg, orderData) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    const order = await createOrder({
      ...orderData,
      clientId: userId,
      status: 'PENDING'
    });
    
    await bot.sendMessage(chatId, `<b>✅ Заказ успешно создан!</b>

${formatOrderInfo(order)}`, {
      parse_mode: 'HTML',
      reply_markup: getMainMenuKeyboard()
    });
    
    // Оповещаем подходящих подрядчиков
    await notifyContractors(bot, order);
  } catch (error) {
    handleTelegramError(error, { method: 'handleCreateOrder', userId, orderData });
    await bot.sendMessage(chatId, 'Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.');
  }
};

/**
 * Оповещает подходящих подрядчиков о новом заказе
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} order - Данные заказа
 */
const notifyContractors = async (bot, order) => {
  try {
    // Получаем всех активных подрядчиков
    const contractors = await prisma.user.findMany({
      where: {
        role: 'CONTRACTOR',
        status: 'Свободен',
        isActive: true
      },
      include: {
        location: true
      }
    });
    
    // Фильтруем подрядчиков по расстоянию
    const nearbyContractors = contractors.filter(contractor => {
      if (!contractor.location || !order.location) return false;
      
      const distance = calculateDistance(
        contractor.location.latitude,
        contractor.location.longitude,
        order.location.latitude,
        order.location.longitude
      );
      
      return distance <= (contractor.workZone?.radius || config.geo.defaultRadius);
    });
    
    // Отправляем уведомления
    for (const contractor of nearbyContractors) {
      const keyboard = createInlineKeyboard([
        [{ text: "✅ Принять заказ", callback_data: `accept_order_${order.id}` }],
        [{ text: "❌ Отклонить", callback_data: `decline_order_${order.id}` }]
      ]);
      
      await bot.sendMessage(contractor.telegramId, `<b>🆕 Новый заказ в вашем районе!</b>

${formatOrderInfo(order)}`, {
        parse_mode: 'HTML',
        reply_markup: keyboard
      });
    }
  } catch (error) {
    handleTelegramError(error, { method: 'notifyContractors', orderId: order.id });
  }
};

/**
 * Обработчик принятия заказа
 * @param {TelegramBot} bot - Экземпляр бота
 * @param {Object} query - Callback query
 */
const handleAcceptOrder = async (bot, query) => {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const orderId = parseInt(query.data.replace('accept_order_', ''));
  
  try {
    const user = await getUserByTelegramId(userId);
    if (!user) {
      throw new Error('Пользователь не найден');
    }
    
    const order = await updateOrderStatus(orderId, 'ACCEPTED');
    if (!order) {
      throw new Error('Заказ не найден или уже принят');
    }
    
    // Уведомляем подрядчика
    await bot.sendMessage(chatId, `<b>✅ Заказ #${orderId} успешно принят!</b>

${formatOrderInfo(order)}`, {
      parse_mode: 'HTML',
      reply_markup: getMainMenuKeyboard()
    });
    
    // Уведомляем клиента
    await bot.sendMessage(order.clientId, `<b>🎉 Ваш заказ #${orderId} принят!</b>

Подрядчик: ${user.name}
Рейтинг: ${'⭐'.repeat(Math.round(user.rating))} (${user.rating.toFixed(1)})
Выполнено заказов: ${user.completedOrders}

${formatOrderInfo(order)}`, {
      parse_mode: 'HTML'
    });
  } catch (error) {
    handleTelegramError(error, { method: 'handleAcceptOrder', userId, orderId });
    await bot.sendMessage(chatId, 'Произошла ошибка при принятии заказа. Пожалуйста, попробуйте позже.');
  }
};

module.exports = {
  handleOrders,
  handleOrderSearch,
  handleCreateOrder,
  handleAcceptOrder
}; 