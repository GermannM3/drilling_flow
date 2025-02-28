/**
 * Точка входа для Vercel Serverless Functions.
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 8080;

// Настройка CORS для обработки запросов от Telegram
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Обработка preflight запросов
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  next();
});

// Обслуживание статических файлов из директории public
app.use(express.static('public', { 
  maxAge: '1d',
  setHeaders: (res, path) => {
    // Явно устанавливаем Content-Type для CSS и других файлов
    if (path.endsWith('.css')) {
      res.setHeader('Content-Type', 'text/css');
    } else if (path.endsWith('.js')) {
      res.setHeader('Content-Type', 'application/javascript');
    } else if (path.endsWith('.html')) {
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
    }
  }
}));

// Важно: используем bodyParser для обработки JSON-запросов от Telegram
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Логирование всех запросов для отладки
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Маршрут для запуска бота
app.get('/api/start-bot', (req, res) => {
  console.log('Получен запрос на запуск бота');
  
  // Проверяем, что бот не отключен в настройках
  if (process.env.DISABLE_BOT === 'True') {
    console.log('Бот отключен в настройках');
    return res.json({
      status: 'error',
      message: 'Бот отключен в настройках',
      timestamp: new Date().toISOString()
    });
  }

  // Подготавливаем переменные окружения для бота
  const env = {
    ...process.env,
    TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
    USE_POLLING: 'True',
    DISABLE_BOT: 'False',
    PATH: process.env.PATH
  };

  console.log('Запуск бота с токеном:', env.TELEGRAM_TOKEN ? env.TELEGRAM_TOKEN.substring(0, 5) + '...' + env.TELEGRAM_TOKEN.substring(env.TELEGRAM_TOKEN.length - 5) : 'не установлен');
  console.log('Текущая директория:', process.cwd());
  
  try {
    // Проверяем существование файла бота
    const botPath = path.join(process.cwd(), 'bot/bot.py');
    if (!fs.existsSync(botPath)) {
      console.error(`Файл бота не найден по пути: ${botPath}`);
      return res.json({
        status: 'error',
        message: 'Файл бота не найден',
        path: botPath,
        timestamp: new Date().toISOString()
      });
    }
    
    console.log(`Файл бота найден: ${botPath}`);
    
    // Используем spawn вместо exec для лучшего контроля процесса
    const botProcess = spawn('python', ['bot/bot.py'], { 
      env,
      shell: true,
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    let stdoutData = '';
    let stderrData = '';
    
    // Собираем вывод из stdout
    botProcess.stdout.on('data', (data) => {
      const output = data.toString();
      stdoutData += output;
      console.log(`Вывод бота: ${output}`);
    });
    
    // Собираем ошибки из stderr
    botProcess.stderr.on('data', (data) => {
      const error = data.toString();
      stderrData += error;
      console.error(`Ошибка бота: ${error}`);
    });
    
    // Обработка ошибок запуска процесса
    botProcess.on('error', (err) => {
      console.error('Ошибка при запуске процесса бота:', err);
      return res.json({
        status: 'error',
        message: `Ошибка запуска бота: ${err.message}`,
        timestamp: new Date().toISOString()
      });
    });
    
    // Отправляем ответ не дожидаясь завершения процесса
    res.json({
      status: 'success',
      message: 'Бот запущен',
      timestamp: new Date().toISOString(),
      token_status: env.TELEGRAM_TOKEN ? 'Токен установлен' : 'Токен отсутствует',
      process_id: botProcess.pid
    });
    
    // Отсоединяем процесс от родителя, чтобы он продолжал работать после завершения запроса
    botProcess.unref();
    
  } catch (error) {
    console.error('Критическая ошибка при запуске бота:', error);
    res.json({
      status: 'error',
      message: `Критическая ошибка: ${error.message}`,
      timestamp: new Date().toISOString()
    });
  }
});

// Обработчик для Telegram webhook без токена в URL
app.post('/webhook', (req, res) => {
  console.log('Получен запрос от Telegram webhook на /webhook');
  console.log('Метод запроса:', req.method);
  console.log('Заголовки запроса:', JSON.stringify(req.headers));
  
  // Для OPTIONS запросов сразу возвращаем успешный ответ
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Проверяем наличие тела запроса
  if (!req.body) {
    console.error('Тело запроса отсутствует или не может быть прочитано');
    return res.status(400).json({ error: 'Request body is missing or cannot be parsed' });
  }
  
  console.log('Тело запроса:', JSON.stringify(req.body).substring(0, 200) + '...');

  // Проверяем, что бот не отключен
  if (process.env.DISABLE_BOT === 'True') {
    console.error('Бот отключен в настройках');
    return res.status(403).json({ error: 'Bot is disabled' });
  }

  // Проверяем наличие данных в запросе
  if (Object.keys(req.body).length === 0) {
    console.error('Пустое тело запроса в webhook');
    return res.status(400).json({ error: 'Empty request body' });
  }

  try {
    // Создаем директорию для временных файлов, если она не существует
    const tmpDir = path.join(process.cwd(), 'tmp');
    if (!fs.existsSync(tmpDir)) {
      fs.mkdirSync(tmpDir, { recursive: true });
    }
    
    // Передаем данные боту через временный файл
    const updateData = req.body;
    const updateFile = path.join(tmpDir, `update_${Date.now()}.json`);
    
    fs.writeFileSync(updateFile, JSON.stringify(updateData, null, 2));
    console.log(`Данные webhook сохранены в файл: ${updateFile}`);
    
    // Проверяем наличие файла process_update.py
    const processUpdatePath = path.join(process.cwd(), 'bot/process_update.py');
    if (!fs.existsSync(processUpdatePath)) {
      console.error(`Файл обработчика webhook не найден: ${processUpdatePath}`);
      return res.status(500).json({ 
        error: 'Webhook handler file not found',
        path: processUpdatePath
      });
    }
    
    // Запускаем обработчик апдейта с передачей файла
    const env = {
      ...process.env,
      TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
      USE_POLLING: 'False',
      DISABLE_BOT: 'False',
      UPDATE_FILE: updateFile,
      PATH: process.env.PATH
    };
    
    console.log('Запуск обработчика webhook с токеном:', env.TELEGRAM_TOKEN ? env.TELEGRAM_TOKEN.substring(0, 5) + '...' : 'не установлен');
    
    const updateProcess = spawn('python', ['bot/process_update.py'], {
      env,
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    // Логируем вывод процесса для отладки
    updateProcess.stdout.on('data', (data) => {
      console.log(`Вывод обработчика webhook: ${data.toString()}`);
    });
    
    updateProcess.stderr.on('data', (data) => {
      console.error(`Ошибка обработчика webhook: ${data.toString()}`);
    });
    
    updateProcess.on('error', (err) => {
      console.error('Ошибка при запуске обработчика webhook:', err);
    });
    
    updateProcess.unref();
    
    // Немедленно отвечаем телеграму успехом
    res.status(200).send('OK');
    console.log('Webhook обработан успешно');
  } catch (error) {
    console.error('Ошибка при обработке webhook:', error);
    res.status(500).json({ error: 'Internal Server Error', message: error.message });
  }
});

// Обработчик для Telegram webhook с токеном в URL
app.post('/webhook/:token', (req, res) => {
  const token = req.params.token;
  
  console.log('Получен запрос от Telegram webhook на /webhook/:token');
  console.log('Метод запроса:', req.method);
  
  // Для OPTIONS запросов сразу возвращаем успешный ответ
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Проверяем, что токен совпадает с нашим
  if (token !== process.env.TELEGRAM_TOKEN) {
    console.error('Неверный токен в запросе вебхука');
    return res.status(403).json({ error: 'Forbidden' });
  }

  // Проверяем, что бот не отключен
  if (process.env.DISABLE_BOT === 'True') {
    console.error('Бот отключен в настройках');
    return res.status(403).json({ error: 'Bot is disabled' });
  }

  // Проверяем наличие данных в запросе
  if (!req.body || Object.keys(req.body).length === 0) {
    console.error('Пустое тело запроса в webhook');
    return res.status(400).json({ error: 'Empty request body' });
  }

  try {
    // Создаем директорию для временных файлов, если она не существует
    const tmpDir = path.join(process.cwd(), 'tmp');
    if (!fs.existsSync(tmpDir)) {
      fs.mkdirSync(tmpDir, { recursive: true });
    }
    
    // Передаем данные боту через временный файл
    const updateData = req.body;
    const updateFile = path.join(tmpDir, `update_${Date.now()}.json`);
    
    fs.writeFileSync(updateFile, JSON.stringify(updateData, null, 2));
    console.log(`Данные webhook сохранены в файл: ${updateFile}`);
    
    // Запускаем обработчик апдейта с передачей файла
    const env = {
      ...process.env,
      TELEGRAM_TOKEN: process.env.TELEGRAM_TOKEN,
      USE_POLLING: 'False',
      DISABLE_BOT: 'False',
      UPDATE_FILE: updateFile,
      PATH: process.env.PATH
    };
    
    const updateProcess = spawn('python', ['bot/process_update.py'], {
      env,
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    // Логируем вывод процесса для отладки
    updateProcess.stdout.on('data', (data) => {
      console.log(`Вывод обработчика webhook: ${data.toString()}`);
    });
    
    updateProcess.stderr.on('data', (data) => {
      console.error(`Ошибка обработчика webhook: ${data.toString()}`);
    });
    
    updateProcess.on('error', (err) => {
      console.error('Ошибка при запуске обработчика webhook:', err);
    });
    
    updateProcess.unref();
    
    // Немедленно отвечаем телеграму успехом
    res.status(200).send('OK');
    console.log('Webhook обработан успешно');
  } catch (error) {
    console.error('Ошибка при обработке вебхука:', error);
    res.status(500).json({ error: 'Internal Server Error', message: error.message });
  }
});

// Маршрут для API информации
app.get('/api', (req, res) => {
  res.json({
    status: 'ok',
    message: 'API работает',
    timestamp: new Date().toISOString(),
    env: {
      NODE_ENV: process.env.NODE_ENV,
      DISABLE_BOT: process.env.DISABLE_BOT,
      USE_POLLING: process.env.USE_POLLING,
      TELEGRAM_TOKEN_STATUS: process.env.TELEGRAM_TOKEN ? 'установлен' : 'не установлен',
      BOT_WEBHOOK_DOMAIN: process.env.BOT_WEBHOOK_DOMAIN || 'не установлен'
    }
  });
});

// Специальный маршрут для CSS файлов
app.get('/style.css', (req, res) => {
  const cssPath = path.join(process.cwd(), 'public', 'style.css');
  
  if (fs.existsSync(cssPath)) {
    res.setHeader('Content-Type', 'text/css');
    res.sendFile(cssPath);
  } else {
    res.status(404).send('CSS file not found');
  }
});

// Маршрут для корневого URL
app.get('/', (req, res) => {
  // Проверяем наличие файла index.html в директории public
  const indexPath = path.join(process.cwd(), 'public', 'index.html');
  
  if (fs.existsSync(indexPath)) {
    // Если файл существует, отправляем его
    res.sendFile(indexPath);
  } else {
    // Если файл не существует, отправляем генерируемую страницу
    res.send(`
      <!DOCTYPE html>
      <html lang="ru">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DrillFlow - Система управления буровыми работами</title>
        <link rel="stylesheet" href="/style.css">
        <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Roboto:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
          tailwind.config = {
            theme: {
              extend: {
                colors: {
                  neutral: {
                    50: "#1D232A",
                    100: "#1C2229",
                    200: "#1B2127",
                    300: "#1A2026",
                    400: "#1A1F25",
                    500: "#191E24",
                    600: "#0C0E11",
                    700: "#090B0D",
                    800: "#060708",
                    900: "#030304",
                    DEFAULT: "#1D232A"
                  },
                  primary: {
                    50: "#f1fcf2",
                    100: "#defae2",
                    200: "#bef4c7",
                    300: "#8bea9c",
                    400: "#51d76a",
                    500: "#2abd46",
                    600: "#1d9c35",
                    700: "#1a7b2d",
                    800: "#1a6128",
                    900: "#175024",
                    950: "#072c0f",
                    DEFAULT: "#2abd46"
                  }
                },
                fontFamily: {
                  sans: ["Oswald", "ui-sans-serif", "system-ui"],
                  title: ["Roboto", "ui-sans-serif", "system-ui"],
                  body: ["Inter", "ui-sans-serif", "system-ui"]
                },
                scale: {
                  '102': '1.02',
                }
              }
            }
          }
        </script>
        <style>
          body {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #1D232A;
            color: #ffffff;
          }
          .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #1A2026;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border: 1px solid #2abd46;
          }
          h1 {
            color: #ffffff;
            font-family: 'Oswald', sans-serif;
          }
          .api-status {
            background-color: #1A2026;
            padding: 10px;
            border-radius: 4px;
            margin-top: 20px;
            border: 1px solid #2abd46;
          }
          .btn-primary {
            display: inline-block;
            margin-top: 20px;
            text-decoration: none;
            background-color: #2abd46;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
          }
          .btn-primary:hover {
            background-color: #1d9c35;
            transform: scale(1.05);
          }
          .status-active {
            color: #2abd46;
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <div class="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-emerald-900 flex items-center justify-center p-4 sm:p-8">
          <div class="w-full max-w-[800px] bg-gradient-to-br from-gray-800/95 via-blue-900/90 to-emerald-900/90 backdrop-blur-md rounded-2xl shadow-[0_0_60px_rgba(0,0,0,0.5)] p-4 sm:p-8 border-2 sm:border-4 border-white/10">
            <header class="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
              <div class="flex items-center gap-4 group">
                <span class="material-symbols-outlined text-4xl sm:text-5xl text-blue-400 transform group-hover:rotate-180 transition-all duration-500 shadow-lg shadow-blue-500/50">water_drop</span>
                <h1 class="text-3xl sm:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">DrillFlow API</h1>
              </div>
            </header>
            
            <div class="bg-gradient-to-br from-gray-800/90 to-blue-900/90 backdrop-blur-md p-6 rounded-2xl border-2 border-blue-500/20 mb-6">
              <p class="text-blue-300 text-lg">Сервер запущен и работает нормально.</p>
              <div class="mt-4 p-4 bg-blue-900/30 rounded-xl border border-blue-500/30">
                <p class="text-blue-300">Статус API: <span class="text-emerald-400 font-bold">Онлайн</span></p>
                <p class="text-blue-300">Время сервера: <span class="text-blue-300">${new Date().toLocaleString('ru-RU')}</span></p>
              </div>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <a href="/api" class="bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900 text-white font-bold py-3 px-4 rounded-xl text-center transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl shadow-blue-500/20 border-2 border-blue-400/30 flex items-center justify-center gap-2">
                <span class="material-symbols-outlined">api</span>
                Информация API
              </a>
              
              <a href="/api/start-bot" class="bg-gradient-to-r from-emerald-600 to-emerald-800 hover:from-emerald-700 hover:to-emerald-900 text-white font-bold py-3 px-4 rounded-xl text-center transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl shadow-emerald-500/20 border-2 border-emerald-400/30 flex items-center justify-center gap-2">
                <span class="material-symbols-outlined">smart_toy</span>
                Запустить бота
              </a>
            </div>
            
            <div class="mt-6">
              <a href="https://t.me/Drill_Flow_bot" target="_blank" class="block w-full bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-700 hover:to-emerald-700 text-white font-bold py-3 px-4 rounded-xl text-center transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl shadow-emerald-500/20 border-2 border-emerald-400/30">
                <span class="flex items-center justify-center gap-2">
                  <span class="material-symbols-outlined">send</span>
                  Открыть Telegram бота
                </span>
              </a>
            </div>
            
            <div class="mt-8 text-center">
              <p class="text-blue-300/70 text-sm">© 2025 DrillFlow. Все права защищены.</p>
            </div>
          </div>
        </div>
      </body>
      </html>
    `);
  }
});

// Обрабатываем 404 ошибки
app.use((req, res, next) => {
  console.log(`404 ошибка для пути: ${req.path}, метод: ${req.method}`);
  
  if (req.path.endsWith('.css')) {
    // Если запрашивается CSS файл, который не найден, попробуем отдать основной CSS
    const mainCss = path.join(process.cwd(), 'public', 'style.css');
    if (fs.existsSync(mainCss)) {
      res.setHeader('Content-Type', 'text/css');
      return res.sendFile(mainCss);
    }
  }
  
  res.status(404).json({
    status: 'error',
    message: 'Страница не найдена',
    path: req.path,
    method: req.method
  });
});

// Обработка ошибок
app.use((err, req, res, next) => {
  console.error('Ошибка сервера:', err);
  res.status(500).json({
    status: 'error',
    message: 'Внутренняя ошибка сервера',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Запуск сервера
if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`Сервер запущен на порту ${port}`);
  });
}

module.exports = app;