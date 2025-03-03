const TelegramBot = require('node-telegram-bot-api');

// Токен из .env файла или жестко заданный
const TOKEN = process.env.TELEGRAM_TOKEN || "7293247588:AAH5qQkNUmhoTzZ-_MSw0gS4BKlSTAW5qdM";

console.log('ТЕСТОВЫЙ БОТ - проверка работы callback-кнопок');
console.log('Токен:', TOKEN);

// Создаем экземпляр бота
const bot = new TelegramBot(TOKEN, {
  polling: true
});

// Проверка соединения
bot.getMe()
  .then(botInfo => {
    console.log('✅ Тестовый бот успешно запущен');
    console.log(`📱 Имя бота: ${botInfo.first_name}`);
    console.log(`👤 Username: @${botInfo.username}`);
  })
  .catch(error => {
    console.error('❌ Ошибка при подключении к API Telegram:', error.message);
    process.exit(1);
  });

// Обработка команды /start
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  
  console.log('Получена команда /start от пользователя:', msg.from.id);
  
  const options = {
    reply_markup: {
      inline_keyboard: [
        [
          { text: "Кнопка 1", callback_data: "button1" },
          { text: "Кнопка 2", callback_data: "button2" }
        ],
        [
          { text: "Кнопка 3", callback_data: "button3" }
        ]
      ]
    }
  };
  
  bot.sendMessage(chatId, "Тестирование callback-кнопок. Нажмите на кнопку:", options)
    .then(() => console.log('Сообщение с кнопками отправлено'))
    .catch(error => console.error('Ошибка при отправке сообщения:', error.message));
});

// Обработка нажатий на кнопки
bot.on('callback_query', (callbackQuery) => {
  const chatId = callbackQuery.message.chat.id;
  const data = callbackQuery.data;
  
  console.log('ПОЛУЧЕН CALLBACK_QUERY:');
  console.log('- От пользователя:', callbackQuery.from.id);
  console.log('- Данные кнопки (data):', data);
  
  // Отвечаем на callback
  bot.answerCallbackQuery(callbackQuery.id)
    .then(() => console.log('answerCallbackQuery выполнен успешно'))
    .catch(error => console.error('Ошибка в answerCallbackQuery:', error.message));
  
  // Отправляем сообщение о том, какая кнопка была нажата
  bot.sendMessage(chatId, `Вы нажали на кнопку с данными: ${data}`)
    .then(() => console.log('Ответ на нажатие отправлен'))
    .catch(error => console.error('Ошибка при отправке ответа:', error.message));
});

// Обработка ошибок
bot.on('polling_error', (error) => {
  console.error('Ошибка в работе бота:', error.message);
});

console.log('Бот запущен! Нажмите Ctrl+C для остановки'); 