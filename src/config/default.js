/**
 * @fileoverview Конфигурация по умолчанию для проекта DrillFlow
 * @module config/default
 */

require('dotenv').config();

module.exports = {
  // Настройки бота
  bot: {
    token: process.env.TELEGRAM_BOT_TOKEN,
    webhookDomain: process.env.BOT_WEBHOOK_DOMAIN || 'https://drilling-flow.vercel.app',
    adminGroupId: process.env.BOT_ADMIN_GROUP_ID || '-1002169340954',
    supportGroupId: process.env.BOT_SUPPORT_GROUP_ID || '-1002169340954'
  },

  // Настройки базы данных
  database: {
    url: process.env.DATABASE_URL,
    maxConnections: 20,
    minConnections: 2,
    connectionTimeout: 30000
  },

  // Настройки сервера
  server: {
    port: process.env.PORT || 3001,
    host: process.env.HOST || '0.0.0.0',
    env: process.env.NODE_ENV || 'development'
  },

  // Настройки геолокации
  geo: {
    defaultRadius: parseInt(process.env.DEFAULT_WORK_RADIUS) || 10,
    maxRadius: parseInt(process.env.MAX_WORK_RADIUS) || 100,
    minRadius: 1
  },

  // Настройки платежей
  payments: {
    currency: 'RUB',
    minAmount: 100,
    maxAmount: 1000000,
    subscriptionPlans: {
      basic: {
        name: 'Базовый',
        price: 990,
        features: [
          'Базовый доступ к заказам',
          'Стандартная статистика',
          'Лимит 5 заказов в день'
        ]
      },
      standard: {
        name: 'Стандартный',
        price: 1990,
        features: [
          'Приоритетное получение заказов',
          'Расширенная статистика',
          'Лимит 10 заказов в день',
          'Техническая поддержка'
        ]
      },
      premium: {
        name: 'Премиум',
        price: 2990,
        features: [
          'Приоритетное получение заказов',
          'Расширенная статистика',
          'Повышенный лимит заказов (до 15 в день)',
          'Персональный менеджер',
          'Бесплатные консультации'
        ]
      }
    }
  },

  // Настройки безопасности
  security: {
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key-here',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN || '24h',
    sessionSecret: process.env.SESSION_SECRET || 'session-secret-key-here',
    rateLimiting: {
      enabled: process.env.RATE_LIMIT_ENABLED === 'true',
      maxRequests: parseInt(process.env.RATE_LIMIT_PER_SECOND) || 100,
      windowMs: 60000 // 1 минута
    }
  },

  // Настройки загрузки файлов
  upload: {
    maxFileSize: process.env.MAX_FILE_SIZE || '10mb',
    allowedTypes: ['image/jpeg', 'image/png', 'application/pdf'],
    uploadDir: process.env.UPLOAD_DIR || 'uploads'
  },

  // Настройки уведомлений
  notifications: {
    defaultEnabled: true,
    types: {
      newOrders: true,
      messages: true,
      statusUpdates: true,
      financialOperations: true,
      emailNotifications: false
    }
  }
}; 