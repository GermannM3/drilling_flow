/**
 * @fileoverview Утилиты для создания клавиатур Telegram бота
 * @module utils/keyboards
 */

const config = require('../config/default');

/**
 * Создает inline-клавиатуру
 * @param {Array<Array<{text: string, callback_data: string}>>} buttons - Массив кнопок
 * @returns {Object} Объект клавиатуры для Telegram
 */
const createInlineKeyboard = (buttons) => ({
  inline_keyboard: buttons
});

/**
 * Создает обычную клавиатуру
 * @param {Array<Array<string>>} buttons - Массив кнопок
 * @param {Object} [options] - Дополнительные опции
 * @returns {Object} Объект клавиатуры для Telegram
 */
const createKeyboard = (buttons, options = {}) => ({
  keyboard: buttons,
  resize_keyboard: true,
  ...options
});

/**
 * Создает главное меню
 * @returns {Object} Клавиатура главного меню
 */
const getMainMenuKeyboard = () => createKeyboard([
  ["📋 Профиль", "📦 Заказы"],
  ["🔍 Поиск заказов", "🔄 Обновить статус"],
  ["📊 Статистика", "💰 Доход"],
  ["⚙️ Настройки", "🔄 Подписка"],
  ["💳 Тестовый платеж", "❓ Помощь"]
]);

/**
 * Создает клавиатуру для профиля
 * @param {Object} user - Данные пользователя
 * @returns {Object} Клавиатура профиля
 */
const getProfileKeyboard = (user) => createInlineKeyboard([
  [{ text: "✏️ Изменить имя", callback_data: "edit_name" }],
  [{ text: "✏️ Изменить телефон", callback_data: "edit_phone" }],
  [{ text: "✏️ Изменить email", callback_data: "edit_email" }],
  [{ text: "✏️ Изменить адрес", callback_data: "edit_address" }],
  [{ text: "🔙 Назад к настройкам", callback_data: "back_to_settings" }]
]);

/**
 * Создает клавиатуру для настроек
 * @param {Object} user - Данные пользователя
 * @returns {Object} Клавиатура настроек
 */
const getSettingsKeyboard = (user) => createInlineKeyboard([
  [{ text: "👤 Редактировать профиль", callback_data: "settings_profile" }],
  [{ text: "🔔 Настройки уведомлений", callback_data: "settings_notifications" }],
  [{ text: "📍 Настройки рабочей зоны", callback_data: "settings_workzone" }],
  [{ text: "🔒 Безопасность", callback_data: "settings_security" }],
  [{ text: "🔙 Назад", callback_data: "back_to_main" }]
]);

/**
 * Создает клавиатуру для подписки
 * @param {Object} user - Данные пользователя
 * @returns {Object} Клавиатура подписки
 */
const getSubscriptionKeyboard = (user) => {
  const { subscriptionPlans } = config.payments;
  
  if (user.subscription?.status === 'ACTIVE') {
    return createInlineKeyboard([
      [{ text: "🔄 Продлить подписку", callback_data: "subscription_extend" }],
      [{ text: "❌ Отменить подписку", callback_data: "subscription_cancel" }],
      [{ text: "🔙 Назад", callback_data: "back_to_main" }]
    ]);
  }
  
  return createInlineKeyboard([
    [{ 
      text: `💰 ${subscriptionPlans.basic.name} (${subscriptionPlans.basic.price} ₽)`, 
      callback_data: "subscription_basic" 
    }],
    [{ 
      text: `💰 ${subscriptionPlans.standard.name} (${subscriptionPlans.standard.price} ₽)`, 
      callback_data: "subscription_standard" 
    }],
    [{ 
      text: `💰 ${subscriptionPlans.premium.name} (${subscriptionPlans.premium.price} ₽)`, 
      callback_data: "subscription_premium" 
    }],
    [{ text: "🔙 Назад", callback_data: "back_to_main" }]
  ]);
};

/**
 * Создает клавиатуру для заказов
 * @param {Array} orders - Массив заказов
 * @returns {Object} Клавиатура заказов
 */
const getOrdersKeyboard = (orders) => {
  const buttons = orders.map(order => ([{
    text: `✅ Принять заказ #${order.id}`,
    callback_data: `accept_order_${order.id}`
  }]));
  
  buttons.push([
    { text: "🔄 Показать все заказы", callback_data: "search_all" }
  ]);
  
  buttons.push([
    { text: "🔙 Назад к поиску", callback_data: "back_to_search" }
  ]);
  
  return createInlineKeyboard(buttons);
};

/**
 * Создает клавиатуру для статусов
 * @returns {Object} Клавиатура статусов
 */
const getStatusKeyboard = () => createInlineKeyboard([
  [
    { text: "✅ Свободен", callback_data: "status_free" },
    { text: "⏳ Занят", callback_data: "status_busy" }
  ],
  [
    { text: "🔄 Перерыв", callback_data: "status_break" },
    { text: "❌ Недоступен", callback_data: "status_unavailable" }
  ],
  [
    { text: "🔙 Назад", callback_data: "back_to_main" }
  ]
]);

/**
 * Создает клавиатуру для тестового платежа
 * @returns {Object} Клавиатура тестового платежа
 */
const getTestPaymentKeyboard = () => createInlineKeyboard([
  [{ text: "💳 Оплатить 100 ₽", callback_data: "pay_test_100" }],
  [{ text: "💳 Оплатить 500 ₽", callback_data: "pay_test_500" }],
  [{ text: "💳 Оплатить 1000 ₽", callback_data: "pay_test_1000" }],
  [{ text: "🔙 Назад", callback_data: "back_to_main" }]
]);

module.exports = {
  createInlineKeyboard,
  createKeyboard,
  getMainMenuKeyboard,
  getProfileKeyboard,
  getSettingsKeyboard,
  getSubscriptionKeyboard,
  getOrdersKeyboard,
  getStatusKeyboard,
  getTestPaymentKeyboard
}; 