/**
 * @fileoverview Централизованная обработка ошибок
 * @module utils/errorHandler
 */

const config = require('../config/default');
const { logError } = require('./common');

/**
 * Типы ошибок
 * @enum {string}
 */
const ErrorTypes = {
  DATABASE: 'DATABASE_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  AUTHENTICATION: 'AUTH_ERROR',
  TELEGRAM_API: 'TELEGRAM_API_ERROR',
  PAYMENT: 'PAYMENT_ERROR',
  GENERAL: 'GENERAL_ERROR'
};

/**
 * Класс пользовательской ошибки
 */
class AppError extends Error {
  /**
   * @param {string} message - Сообщение об ошибке
   * @param {string} type - Тип ошибки из enum ErrorTypes
   * @param {Object} [details] - Дополнительные детали ошибки
   */
  constructor(message, type = ErrorTypes.GENERAL, details = {}) {
    super(message);
    this.name = 'AppError';
    this.type = type;
    this.details = details;
    this.timestamp = new Date().toISOString();
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Обработчик ошибок базы данных
 * @param {Error} error - Объект ошибки
 * @param {Object} context - Контекст ошибки
 * @returns {AppError} Обработанная ошибка
 */
const handleDatabaseError = (error, context = {}) => {
  const appError = new AppError(
    'Ошибка при работе с базой данных',
    ErrorTypes.DATABASE,
    { originalError: error.message, ...context }
  );
  
  logError(appError, {
    component: 'Database',
    query: context.query,
    params: context.params
  });
  
  return appError;
};

/**
 * Обработчик ошибок валидации
 * @param {Error} error - Объект ошибки
 * @param {Object} context - Контекст ошибки
 * @returns {AppError} Обработанная ошибка
 */
const handleValidationError = (error, context = {}) => {
  const appError = new AppError(
    'Ошибка валидации данных',
    ErrorTypes.VALIDATION,
    { originalError: error.message, ...context }
  );
  
  logError(appError, {
    component: 'Validation',
    invalidFields: context.invalidFields
  });
  
  return appError;
};

/**
 * Обработчик ошибок аутентификации
 * @param {Error} error - Объект ошибки
 * @param {Object} context - Контекст ошибки
 * @returns {AppError} Обработанная ошибка
 */
const handleAuthError = (error, context = {}) => {
  const appError = new AppError(
    'Ошибка аутентификации',
    ErrorTypes.AUTHENTICATION,
    { originalError: error.message, ...context }
  );
  
  logError(appError, {
    component: 'Authentication',
    userId: context.userId
  });
  
  return appError;
};

/**
 * Обработчик ошибок Telegram API
 * @param {Error} error - Объект ошибки
 * @param {Object} context - Контекст ошибки
 * @returns {AppError} Обработанная ошибка
 */
const handleTelegramError = (error, context = {}) => {
  const appError = new AppError(
    'Ошибка при работе с Telegram API',
    ErrorTypes.TELEGRAM_API,
    { originalError: error.message, ...context }
  );
  
  logError(appError, {
    component: 'TelegramAPI',
    method: context.method,
    params: context.params
  });
  
  return appError;
};

/**
 * Обработчик ошибок платежей
 * @param {Error} error - Объект ошибки
 * @param {Object} context - Контекст ошибки
 * @returns {AppError} Обработанная ошибка
 */
const handlePaymentError = (error, context = {}) => {
  const appError = new AppError(
    'Ошибка при обработке платежа',
    ErrorTypes.PAYMENT,
    { originalError: error.message, ...context }
  );
  
  logError(appError, {
    component: 'Payment',
    paymentId: context.paymentId,
    amount: context.amount
  });
  
  return appError;
};

/**
 * Глобальный обработчик необработанных ошибок
 * @param {Error} error - Объект ошибки
 */
const handleUncaughtError = (error) => {
  const appError = new AppError(
    'Необработанная ошибка приложения',
    ErrorTypes.GENERAL,
    { originalError: error.message }
  );
  
  logError(appError, {
    component: 'UncaughtException',
    environment: config.server.env
  });
  
  // В production не показываем детали ошибки
  if (config.server.env === 'production') {
    return new AppError('Внутренняя ошибка сервера');
  }
  
  return appError;
};

// Регистрируем глобальные обработчики
process.on('uncaughtException', handleUncaughtError);
process.on('unhandledRejection', (reason) => {
  handleUncaughtError(reason instanceof Error ? reason : new Error(String(reason)));
});

module.exports = {
  ErrorTypes,
  AppError,
  handleDatabaseError,
  handleValidationError,
  handleAuthError,
  handleTelegramError,
  handlePaymentError,
  handleUncaughtError
}; 