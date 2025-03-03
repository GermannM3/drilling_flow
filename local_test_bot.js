// Скрипт для локального тестирования Telegram бота
const express = require('express');
const bodyParser = require('body-parser');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Загружаем переменные окружения из .env файла
require('dotenv').config();

// Импортируем обработчик вебхука из новой совместимой версии
const botHandler = require('./api/telegram_webhook_handler.js').default;

// Создаем Express приложение
const app = express();

// Настройка middleware
app.use(bodyParser.json());

// Логирование всех запросов к Telegram API
const originalRequest = https.request;
https.request = function(options, callback) {
  // Проверяем, что запрос идет к API Telegram
  const urlString = typeof options === 'string' ? options : 
                    options.href || (options.protocol ? `${options.protocol}//${options.hostname}${options.path}` : null);
                    
  if (urlString && urlString.includes('api.telegram.org')) {
    console.log('\nОтправка запроса к Telegram API:');
    console.log('URL:', urlString);
    
    if (options.method === 'POST' && options.headers && options.headers['Content-Type'] === 'application/json') {
      const requestCallback = callback;
      callback = function(res) {
        console.log(`Статус ответа от Telegram API: ${res.statusCode}`);
        
        let data = '';
        res.on('data', chunk => {
          data += chunk;
        });
        
        res.on('end', () => {
          try {
            const responseData = JSON.parse(data);
            console.log('Ответ от Telegram API:');
            console.log(JSON.stringify(responseData, null, 2));
          } catch (e) {
            console.log('Ошибка парсинга ответа от Telegram API:', e.message);
          }
        });
        
        if (requestCallback) {
          requestCallback(res);
        }
      };
    }
  }
  
  return originalRequest.apply(this, arguments);
};

// Маршрут для вебхука
app.post('/webhook', async (req, res) => {
  console.log('Получен POST-запрос на /webhook:');
  console.log('Тело запроса:', JSON.stringify(req.body, null, 2));
  
  try {
    // Передаем запрос обработчику
    await botHandler(req, res);
  } catch (error) {
    console.error('Ошибка при обработке вебхука:', error);
    res.status(500).json({ 
      error: 'Внутренняя ошибка сервера', 
      message: error.message 
    });
  }
});

// Маршрут для проверки работоспособности
app.get('/webhook', async (req, res) => {
  console.log('Получен GET-запрос на /webhook');
  await botHandler(req, res);
});

// Тестовый маршрут
app.get('/', (req, res) => {
  res.json({
    status: 'Тестовый сервер DrillFlow работает',
    webhook_url: `http://localhost:3001/webhook`,
    time: new Date().toISOString()
  });
});

// Маршрут для проверки статуса сервера
app.get('/status', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// Порт для прослушивания
const PORT = 3001;

// Запуск сервера
app.listen(PORT, () => {
  console.log(`Локальный сервер запущен на порту ${PORT}`);
  console.log(`Вебхук доступен по адресу: http://localhost:${PORT}/webhook`);
  console.log('\nДля тестирования отправки сообщения можно использовать:');
  console.log(`curl -X POST -H "Content-Type: application/json" -d '{"update_id":123456789,"message":{"message_id":123,"from":{"id":1234567,"first_name":"Тест","username":"testuser"},"chat":{"id":1234567,"first_name":"Тест","username":"testuser","type":"private"},"date":1679000000,"text":"/start"}}' http://localhost:${PORT}/webhook`);
  console.log('\nИли отправкой команды "📋 Профиль":');
  console.log(`curl -X POST -H "Content-Type: application/json" -d '{"update_id":123456789,"message":{"message_id":123,"from":{"id":1234567,"first_name":"Тест","username":"testuser"},"chat":{"id":1234567,"first_name":"Тест","username":"testuser","type":"private"},"date":1679000000,"text":"📋 Профиль"}}' http://localhost:${PORT}/webhook`);
});

// Обработка процесса завершения
process.on('SIGINT', () => {
  console.log('\n👋 Завершение работы сервера...');
  process.exit(0);
});