/**
 * Точка входа для Vercel Serverless Functions.
 */

// Импортируем необходимые модули
const fs = require('fs');
const path = require('path');

/**
 * Обработчик запросов для Vercel
 */
module.exports = (req, res) => {
  // Устанавливаем заголовки
  res.setHeader('Content-Type', 'text/html');
  
  // Отправляем простую HTML страницу
  res.status(200).send(`
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>DrillFlow - Сервис бурения скважин</title>
      <style>
        body {
          font-family: 'Arial', sans-serif;
          line-height: 1.6;
          margin: 0;
          padding: 20px;
          color: #333;
          background: #f5f5f5;
        }
        .container {
          max-width: 800px;
          margin: 0 auto;
          background: white;
          padding: 20px;
          border-radius: 5px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
          color: #2c3e50;
          border-bottom: 2px solid #3498db;
          padding-bottom: 10px;
        }
        .status {
          display: inline-block;
          background: #2ecc71;
          color: white;
          padding: 5px 10px;
          border-radius: 3px;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>DrillFlow API</h1>
        <p>Статус сервера: <span class="status">Онлайн</span></p>
        <p>Это временная страница для проверки работоспособности сервера.</p>
        <p>Дата и время: ${new Date().toLocaleString('ru-RU')}</p>
      </div>
    </body>
    </html>
  `);
}; 