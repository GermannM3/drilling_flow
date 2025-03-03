// Скрипт для тестирования команд Telegram бота
const https = require('https');

// ID чата для тестирования (можно заменить на свой)
const CHAT_ID = 7129776749;
const userId = CHAT_ID;

// Функция для отправки тестового сообщения на локальный сервер бота
function sendTestMessage(text) {
  const testData = {
    update_id: Math.floor(Math.random() * 1000000),
    message: {
      message_id: Math.floor(Math.random() * 10000),
      from: {
        id: userId,
        first_name: "Тестер",
        username: "Tester"
      },
      chat: {
        id: CHAT_ID,
        first_name: "Тестер",
        username: "Tester",
        type: "private"
      },
      date: Math.floor(Date.now() / 1000),
      text: text
    }
  };

  const data = JSON.stringify(testData);
  
  const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/webhook',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        resolve(responseData);
      });
    });
    
    req.on('error', (error) => {
      console.error('Ошибка отправки тестового сообщения:', error);
      reject(error);
    });
    
    req.write(data);
    req.end();
  });
}

// Функция для последовательной отправки всех тестовых команд
async function testAllCommands() {
  const commands = [
    '/start',
    '📋 Профиль',
    '📦 Заказы',
    '🔄 Обновить статус',
    '📊 Статистика',
    '💰 Доход',
    '⚙️ Настройки',
    '🔄 Подписка',
    '💳 Тестовый платеж',
    '❓ Помощь'
  ];
  
  console.log('Начинаю тестирование всех команд бота...\n');
  
  for (const command of commands) {
    console.log(`Отправка команды: "${command}"`);
    try {
      await sendTestMessage(command);
      console.log(`✅ Команда "${command}" отправлена успешно`);
    } catch (error) {
      console.error(`❌ Ошибка при отправке команды "${command}":`, error);
    }
    
    // Задержка между командами для более удобного тестирования
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log('\nТестирование всех команд завершено!');
}

// Запуск тестирования
testAllCommands().catch(console.error); 