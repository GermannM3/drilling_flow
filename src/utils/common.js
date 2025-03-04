/**
 * @fileoverview Общие утилиты для проекта DrillFlow
 * @module utils/common
 */

const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

/**
 * Преобразует градусы в радианы
 * @param {number} degrees - Значение в градусах
 * @returns {number} Значение в радианах
 */
const toRadians = (degrees) => degrees * Math.PI / 180;

/**
 * Вычисляет расстояние между двумя точками на карте
 * @param {number} lat1 - Широта первой точки
 * @param {number} lon1 - Долгота первой точки
 * @param {number} lat2 - Широта второй точки
 * @param {number} lon2 - Долгота второй точки
 * @returns {number} Расстояние в километрах
 */
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371; // Радиус Земли в км
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};

/**
 * Форматирует денежную сумму
 * @param {number} amount - Сумма
 * @param {string} [currency='₽'] - Валюта
 * @returns {string} Отформатированная строка
 */
const formatCurrency = (amount, currency = '₽') => {
  return `${amount.toLocaleString('ru-RU')} ${currency}`;
};

/**
 * Создает базовую inline-клавиатуру
 * @param {Array<Array<{text: string, callback_data: string}>>} buttons - Массив кнопок
 * @returns {Object} Объект клавиатуры для Telegram
 */
const createInlineKeyboard = (buttons) => ({
  inline_keyboard: buttons
});

/**
 * Форматирует дату в российском формате
 * @param {Date} date - Дата для форматирования
 * @returns {string} Отформатированная дата
 */
const formatDate = (date) => {
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

/**
 * Получает правильное окончание для числительных
 * @param {number} count - Количество
 * @param {Array<string>} words - Массив вариантов слова [один, два-четыре, много]
 * @returns {string} Правильная форма слова
 */
const getWordForm = (count, words) => {
  const cases = [2, 0, 1, 1, 1, 2];
  return words[
    count % 100 > 4 && count % 100 < 20 
      ? 2 
      : cases[Math.min(count % 10, 5)]
  ];
};

/**
 * Создает стандартную клавиатуру для возврата в главное меню
 * @returns {Object} Объект клавиатуры
 */
const getBackToMainKeyboard = () => createInlineKeyboard([
  [{ text: "🔙 Вернуться в главное меню", callback_data: "back_to_main" }]
]);

/**
 * Проверяет валидность email
 * @param {string} email - Email для проверки
 * @returns {boolean} Результат проверки
 */
const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

/**
 * Проверяет валидность номера телефона
 * @param {string} phone - Номер телефона
 * @returns {boolean} Результат проверки
 */
const isValidPhone = (phone) => {
  const re = /^(\+7|8)?[\s-]?\(?[489][0-9]{2}\)?[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}$/;
  return re.test(phone);
};

/**
 * Логирует ошибку с дополнительным контекстом
 * @param {Error} error - Объект ошибки
 * @param {Object} context - Контекст ошибки
 */
const logError = (error, context = {}) => {
  console.error('❌ Ошибка:', {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString(),
    ...context
  });
};

/**
 * Безопасно выполняет асинхронную операцию с базой данных
 * @param {Function} operation - Асинхронная операция
 * @param {Object} errorContext - Контекст для логирования ошибки
 * @returns {Promise<*>} Результат операции или null в случае ошибки
 */
const safeDbOperation = async (operation, errorContext = {}) => {
  try {
    return await operation();
  } catch (error) {
    logError(error, errorContext);
    return null;
  }
};

module.exports = {
  calculateDistance,
  formatCurrency,
  createInlineKeyboard,
  formatDate,
  getWordForm,
  getBackToMainKeyboard,
  isValidEmail,
  isValidPhone,
  logError,
  safeDbOperation
}; 