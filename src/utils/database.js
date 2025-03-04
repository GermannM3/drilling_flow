/**
 * @fileoverview Утилиты для работы с базой данных
 * @module utils/database
 */

const { PrismaClient } = require('@prisma/client');
const NodeCache = require('node-cache');
const { handleDatabaseError } = require('./errorHandler');
const config = require('../config/default');

// Инициализация Prisma Client
const prisma = new PrismaClient({
  log: config.server.env === 'development' ? ['query', 'info', 'warn', 'error'] : ['error'],
  errorFormat: 'pretty'
});

// Инициализация кэша
const cache = new NodeCache({
  stdTTL: 300, // 5 минут
  checkperiod: 60, // Проверка устаревших записей каждую минуту
  useClones: false
});

/**
 * Генерирует ключ кэша для заданных параметров
 * @param {string} entity - Название сущности
 * @param {string|number} id - Идентификатор
 * @param {string} [action='get'] - Действие
 * @returns {string} Ключ кэша
 */
const getCacheKey = (entity, id, action = 'get') => `${entity}:${id}:${action}`;

/**
 * Получает данные из кэша или базы данных
 * @param {string} entity - Название сущности
 * @param {string|number} id - Идентификатор
 * @param {Function} dbFetch - Функция получения данных из БД
 * @returns {Promise<*>} Данные из кэша или БД
 */
const getFromCacheOrDb = async (entity, id, dbFetch) => {
  const cacheKey = getCacheKey(entity, id);
  const cachedData = cache.get(cacheKey);
  
  if (cachedData) {
    return cachedData;
  }
  
  try {
    const data = await dbFetch();
    if (data) {
      cache.set(cacheKey, data);
    }
    return data;
  } catch (error) {
    throw handleDatabaseError(error, { entity, id });
  }
};

/**
 * Очищает кэш для заданной сущности
 * @param {string} entity - Название сущности
 * @param {string|number} id - Идентификатор
 */
const invalidateCache = (entity, id) => {
  const pattern = new RegExp(`^${entity}:${id}:`);
  const keys = cache.keys().filter(key => pattern.test(key));
  cache.del(keys);
};

/**
 * Получает пользователя по Telegram ID
 * @param {number} telegramId - Telegram ID пользователя
 * @returns {Promise<Object>} Данные пользователя
 */
const getUserByTelegramId = (telegramId) => {
  return getFromCacheOrDb('user', telegramId, () =>
    prisma.user.findUnique({
      where: { telegramId },
      include: {
        location: true,
        settings: true,
        subscription: true
      }
    })
  );
};

/**
 * Обновляет данные пользователя
 * @param {number} telegramId - Telegram ID пользователя
 * @param {Object} data - Данные для обновления
 * @returns {Promise<Object>} Обновленные данные пользователя
 */
const updateUser = async (telegramId, data) => {
  try {
    const updated = await prisma.user.update({
      where: { telegramId },
      data,
      include: {
        location: true,
        settings: true,
        subscription: true
      }
    });
    
    invalidateCache('user', telegramId);
    return updated;
  } catch (error) {
    throw handleDatabaseError(error, { telegramId, data });
  }
};

/**
 * Получает активные заказы для подрядчика
 * @param {number} contractorId - ID подрядчика
 * @returns {Promise<Array>} Список заказов
 */
const getActiveOrders = (contractorId) => {
  return getFromCacheOrDb('orders', contractorId, () =>
    prisma.order.findMany({
      where: {
        contractorId,
        status: 'ACTIVE'
      },
      include: {
        client: true,
        location: true
      }
    })
  );
};

/**
 * Создает новый заказ
 * @param {Object} orderData - Данные заказа
 * @returns {Promise<Object>} Созданный заказ
 */
const createOrder = async (orderData) => {
  try {
    const order = await prisma.order.create({
      data: orderData,
      include: {
        client: true,
        location: true
      }
    });
    
    // Инвалидируем кэш для связанных сущностей
    invalidateCache('orders', orderData.clientId);
    if (orderData.contractorId) {
      invalidateCache('orders', orderData.contractorId);
    }
    
    return order;
  } catch (error) {
    throw handleDatabaseError(error, { orderData });
  }
};

/**
 * Обновляет статус заказа
 * @param {number} orderId - ID заказа
 * @param {string} status - Новый статус
 * @returns {Promise<Object>} Обновленный заказ
 */
const updateOrderStatus = async (orderId, status) => {
  try {
    const order = await prisma.order.update({
      where: { id: orderId },
      data: { status },
      include: {
        client: true,
        contractor: true
      }
    });
    
    // Инвалидируем кэш для всех связанных сущностей
    invalidateCache('orders', order.clientId);
    if (order.contractorId) {
      invalidateCache('orders', order.contractorId);
    }
    
    return order;
  } catch (error) {
    throw handleDatabaseError(error, { orderId, status });
  }
};

// Экспортируем функции для работы с БД
module.exports = {
  prisma,
  getUserByTelegramId,
  updateUser,
  getActiveOrders,
  createOrder,
  updateOrderStatus,
  invalidateCache
}; 