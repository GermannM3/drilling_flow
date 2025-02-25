/**
 * Точка входа для Vercel Serverless Functions.
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const app = express();
const port = process.env.PORT || 3000;

// Обслуживание статических файлов из директории public
app.use(express.static('public'));

// Маршрут для запуска бота
app.get('/api/start-bot', (req, res) => {
  // Проверяем, что бот не отключен в настройках
  if (process.env.DISABLE_BOT === 'True') {
    return res.json({
      status: 'error',
      message: 'Бот отключен в настройках',
      timestamp: new Date().toISOString()
    });
  }

  // Подготавливаем переменные окружения для бота
  const env = {
    ...process.env,
    TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN || '7554540052:AAEvde_xL9d85kbJBdxPu8B6Mo4UEMF-qBs',
    USE_POLLING: 'True',
    DISABLE_BOT: 'False'
  };

  console.log('Запуск бота с токеном:', env.TELEGRAM_TOKEN);

  // Запускаем бот через Python
  const botProcess = exec('python bot/bot.py', { env }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Ошибка запуска бота: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Stderr: ${stderr}`);
      return;
    }
    console.log(`Stdout: ${stdout}`);
  });

  // Устанавливаем обработчики событий для процесса
  botProcess.on('error', (err) => {
    console.error('Ошибка при запуске процесса бота:', err);
  });

  // Отправляем ответ
  res.json({
    status: 'success',
    message: 'Бот запущен',
    timestamp: new Date().toISOString(),
    token_status: env.TELEGRAM_TOKEN ? 'Токен установлен' : 'Токен отсутствует'
  });
});

// Маршрут для корневого URL
app.get('/', (req, res) => {
  // Проверяем наличие файла index.html в директории public
  const indexPath = path.join(process.cwd(), 'public', 'index.html');
  
  if (fs.existsSync(indexPath)) {
    // Если файл существует, отправляем его
    res.sendFile(indexPath);
  } else {
    // Если файл не существует, генерируем HTML на лету
    const html = `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DrillFlow - Система управления буровыми работами</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #2c3e50;
                color: white;
                padding: 1rem 0;
                text-align: center;
            }
            .hero {
                background-color: #3498db;
                color: white;
                padding: 3rem 0;
                text-align: center;
            }
            .hero h1 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            .hero p {
                font-size: 1.2rem;
                max-width: 800px;
                margin: 0 auto;
            }
            .features {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin: 2rem 0;
            }
            .feature {
                flex: 1;
                min-width: 300px;
                background: white;
                margin: 1rem;
                padding: 1.5rem;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .feature h3 {
                color: #2c3e50;
                margin-top: 0;
            }
            footer {
                background-color: #2c3e50;
                color: white;
                text-align: center;
                padding: 1rem 0;
                margin-top: 2rem;
            }
            .status {
                background-color: #27ae60;
                color: white;
                padding: 0.5rem;
                border-radius: 4px;
                display: inline-block;
                margin-top: 1rem;
            }
            .cta-button {
                display: inline-block;
                background-color: #e74c3c;
                color: white;
                padding: 0.8rem 1.5rem;
                margin-top: 1rem;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            .cta-button:hover {
                background-color: #c0392b;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <h2>DrillFlow</h2>
            </div>
        </header>
        
        <section class="hero">
            <div class="container">
                <h1>Система управления буровыми работами</h1>
                <p>Эффективное управление буровыми работами, мониторинг и аналитика в режиме реального времени</p>
                <div class="status">Сервер онлайн: ${new Date().toLocaleString('ru-RU')}</div>
                <p><a href="/api/docs" class="cta-button">API Документация</a></p>
            </div>
        </section>
        
        <div class="container">
            <section class="features">
                <div class="feature">
                    <h3>Мониторинг в реальном времени</h3>
                    <p>Отслеживайте все параметры буровых работ в режиме реального времени с помощью интуитивно понятного интерфейса.</p>
                </div>
                <div class="feature">
                    <h3>Аналитика и отчеты</h3>
                    <p>Получайте детальную аналитику и формируйте отчеты для оптимизации процессов и снижения затрат.</p>
                </div>
                <div class="feature">
                    <h3>Управление ресурсами</h3>
                    <p>Эффективно управляйте персоналом, оборудованием и материалами для максимальной производительности.</p>
                </div>
            </section>
        </div>
        
        <footer>
            <div class="container">
                <p>&copy; ${new Date().getFullYear()} DrillFlow. Все права защищены.</p>
            </div>
        </footer>
    </body>
    </html>
    `;
    
    res.setHeader('Content-Type', 'text/html');
    res.send(html);
  }
});

// Маршрут для API
app.get('/api', (req, res) => {
  res.json({
    status: 'online',
    message: 'DrillFlow API работает',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Обработка всех остальных маршрутов
app.get('*', (req, res) => {
  res.redirect('/');
});

// Для локального запуска
if (require.main === module) {
  app.listen(port, () => {
    console.log(`Сервер запущен на порту ${port}`);
  });
}

// Экспорт для Vercel
module.exports = app; 