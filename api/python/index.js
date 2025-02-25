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

// Обслуживание статических файлов из директории public
app.use(express.static('public'));
app.use(bodyParser.json());

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

// Обработчик для Telegram webhook
app.post('/webhook/:token', (req, res) => {
  const token = req.params.token;
  
  // Проверяем, что токен совпадает с нашим
  if (token !== process.env.TELEGRAM_TOKEN) {
    console.error('Неверный токен в запросе вебхука');
    return res.status(403).json({ error: 'Forbidden' });
  }
  
  console.log('Получен запрос от Telegram webhook');
  
  // Передаем данные боту через временный файл
  const updateData = req.body;
  const updateFile = path.join(process.cwd(), 'update.json');
  
  try {
    fs.writeFileSync(updateFile, JSON.stringify(updateData, null, 2));
    
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
      stdio: 'ignore'
    });
    
    updateProcess.unref();
    
    // Немедленно отвечаем телеграму успехом
    res.status(200).send('OK');
    
  } catch (error) {
    console.error('Ошибка при обработке вебхука:', error);
    res.status(500).json({ error: 'Internal Server Error' });
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
      TELEGRAM_TOKEN_STATUS: process.env.TELEGRAM_TOKEN ? 'установлен' : 'не установлен'
    }
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
    // Если файл не существует, отправляем простую страницу
    res.send('Сервер DrillFlow работает. <a href="/api">API информация</a>');
  }
});

// Запуск сервера
if (require.main === module) {
  app.listen(port, () => {
    console.log(`Сервер запущен на порту ${port}`);
  });
}

// Для Vercel
module.exports = app; 