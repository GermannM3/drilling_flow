// Обработчик для вебхука Telegram на Vercel
const https = require('https');

// Получаем токен из переменных окружения 
// Для продакшена - 7554540052:AAEvde_xL9d85kbJBdxPu8B6Mo4UEMF-qBs
// Для локального тестирования - 7293247588:AAH5qQkNUmhoTzZ-_MSw0gS4BKlSTAW5qdM
const TOKEN = process.env.TELEGRAM_TOKEN || "7293247588:AAH5qQkNUmhoTzZ-_MSw0gS4BKlSTAW5qdM";

// Функция для отправки сообщения в Telegram
async function sendTelegramMessage(chatId, text, options = {}) {
  const data = JSON.stringify({
    chat_id: chatId,
    text: text,
    parse_mode: options.parse_mode || 'HTML',
    reply_markup: options.reply_markup
  });

  const apiUrl = `https://api.telegram.org/bot${TOKEN}/sendMessage`;
  
  return new Promise((resolve, reject) => {
    const req = https.request(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    }, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsedData = JSON.parse(responseData);
          resolve(parsedData);
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', (error) => {
      console.error('Ошибка отправки сообщения в Telegram:', error);
      reject(error);
    });
    
    req.write(data);
    req.end();
  });
}

// Получить клавиатуру для главного меню
function getMainMenuKeyboard() {
  return {
    keyboard: [
      [{ text: "📋 Профиль" }, { text: "📦 Заказы" }],
      [{ text: "🔄 Обновить статус" }, { text: "📊 Статистика" }],
      [{ text: "💰 Доход" }, { text: "⚙️ Настройки" }],
      [{ text: "🔄 Подписка" }, { text: "💳 Тестовый платеж" }],
      [{ text: "❓ Помощь" }]
    ],
    resize_keyboard: true
  };
}

// Получить профиль пользователя (заглушка)
function getUserProfileText(userId) {
  return `
<b>👤 Профиль пользователя</b>

🆔 ID: ${userId}
📱 Статус: <b>Активен</b>
📅 Дата регистрации: ${new Date().toLocaleDateString('ru-RU')}

<b>📊 Статистика:</b>
✅ Выполненных заказов: 0
💰 Заработано всего: 0₽
⭐ Рейтинг: не определён

<i>Используйте кнопки ниже для навигации</i>
`;
}

// Получить текст помощи
function getHelpText() {
  return `
<b>❓ Помощь</b>

<b>Основные команды:</b>
📋 <b>Профиль</b> - просмотр вашего профиля
📦 <b>Заказы</b> - список доступных заказов
🔄 <b>Обновить статус</b> - обновить свой статус
📊 <b>Статистика</b> - просмотр вашей статистики
💰 <b>Доход</b> - информация о заработке
⚙️ <b>Настройки</b> - настройки профиля

<b>Дополнительные команды:</b>
🔄 <b>Подписка</b> - управление подпиской
💳 <b>Тестовый платеж</b> - тестирование системы оплаты

<i>Если у вас возникли вопросы, напишите в поддержку: @support</i>
`;
}

// Получить информацию о заказах
function getOrdersText() {
  return `
<b>📦 Ваши заказы</b>

В настоящее время у вас нет активных заказов.

<i>Как только появятся новые заказы, вы получите уведомление.</i>
`;
}

// Получить статистику
function getStatisticsText(userId) {
  return `
<b>📊 Статистика</b>

🆔 Пользователь: ${userId}
📅 Период: <b>Март 2025</b>

<b>Показатели:</b>
✅ Выполнено заказов: 0
❌ Отменено заказов: 0
⏳ В обработке: 0
⭐ Средний рейтинг: N/A

<b>Эффективность:</b>
⚡ Скорость выполнения: N/A
📈 Динамика роста: 0%

<i>Подробную статистику можно увидеть в личном кабинете</i>
`;
}

// Текст для подписки
function getSubscriptionText() {
  return `
<b>🔄 Управление подпиской</b>

Ваш текущий тариф: <b>Базовый</b>
Статус: <b>Активна</b>
Действует до: <b>01.04.2025</b>

<b>Доступные тарифы:</b>
💎 <b>Премиум</b> - 999₽/месяц
  • Приоритет в получении заказов
  • Расширенная статистика
  • Поддержка 24/7

🚀 <b>Профессионал</b> - 1999₽/месяц
  • Все преимущества Премиум
  • Отсутствие комиссии
  • Персональный менеджер

<i>Для изменения тарифа нажмите соответствующую кнопку</i>
`;
}

// Текст для тестового платежа
function getTestPaymentText() {
  return `
<b>💳 Тестовый платеж</b>

Это демонстрация работы платежной системы.

<b>Сумма к оплате:</b> 1₽
<b>Назначение:</b> Тестовый платеж

<i>Нажмите кнопку ниже для перехода к оплате</i>
`;
}

// Клавиатура для тестового платежа
function getTestPaymentKeyboard() {
  return {
    inline_keyboard: [
      [{ text: "💳 Оплатить", callback_data: "pay_test_1" }],
      [{ text: "🔙 Назад", callback_data: "back_to_main" }]
    ]
  };
}

// Получить информацию о доходе
function getIncomeText(userId) {
  return `
<b>💰 Информация о доходе</b>

🆔 Пользователь: ${userId}
📅 Период: <b>Март 2025</b>

<b>Финансы:</b>
💵 Заработано: 0₽
💸 Комиссия сервиса: 0₽
💼 Чистая прибыль: 0₽

<b>Платежная информация:</b>
🏦 Способ вывода: Не указан
📊 Статус выплат: Не активен

<i>Для настройки способа вывода средств перейдите в настройки</i>
`;
}

// Получить текст настроек
function getSettingsText() {
  return `
<b>⚙️ Настройки</b>

<b>Общие настройки:</b>
🔔 Уведомления: <b>Включены</b>
🗣️ Язык: <b>Русский</b>
🌐 Регион: <b>Россия</b>

<b>Профиль:</b>
👤 Видимость профиля: <b>Открытый</b>
🔑 Безопасность: <b>Стандартная</b>

<b>Платежи:</b>
💳 Способ оплаты: <b>Не указан</b>
💰 Способ вывода: <b>Не указан</b>

<i>Для изменения настроек используйте кнопки ниже</i>
`;
}

// Обработка обновления статуса
function getStatusUpdateText() {
  return `<b>🔄 Обновление статуса</b>

Здесь вы можете обновить статус текущих работ.

Статус последнего обновления: 2 часа назад
Текущий статус: В работе

Введите новый статус или выберите из предложенных вариантов.`;
}

module.exports = {
  default: async function handler(req, res) {
    if (req.method === 'GET') {
      // Обработка GET-запроса (для проверки вебхука)
      const response = {
        app: "DrillFlow Bot",
        version: "1.0.0",
        status: "running",
        webhook_url: "https://drilling-flow.vercel.app/api/telegram_bot_webhook",
        telegram_bot: "@Drill_Flow_bot",
        updated_at: new Date().toISOString(),
        version_tag: "v2023-10-21-04",
        handler_file: "telegram_bot_webhook.js"
      };
      
      res.status(200).json(response);
    } else if (req.method === 'POST') {
      // Обработка POST-запроса от Telegram
      console.log('Received webhook data:', req.body);
      
      try {
        const update = req.body;
        
        // Проверяем, что есть сообщение и текст
        if (update && update.message && update.message.text) {
          const chatId = update.message.chat.id;
          const text = update.message.text;
          const userId = update.message.from.id;
          
          // Обрабатываем команды
          switch (text) {
            case '📋 Профиль':
              const profileText = getUserProfileText(userId);
              await sendTelegramMessage(chatId, profileText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлен профиль пользователю ${userId}`);
              break;
              
            case '📦 Заказы':
              const ordersText = getOrdersText();
              await sendTelegramMessage(chatId, ordersText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлена информация о заказах пользователю ${userId}`);
              break;
              
            case '📊 Статистика':
              const statsText = getStatisticsText(userId);
              await sendTelegramMessage(chatId, statsText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлена статистика пользователю ${userId}`);
              break;
              
            case '🔄 Подписка':
              const subscriptionText = getSubscriptionText();
              await sendTelegramMessage(chatId, subscriptionText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлена информация о подписке пользователю ${userId}`);
              break;
              
            case '💳 Тестовый платеж':
              const paymentText = getTestPaymentText();
              await sendTelegramMessage(chatId, paymentText, {
                reply_markup: getTestPaymentKeyboard()
              });
              console.log(`Отправлена информация о тестовом платеже пользователю ${userId}`);
              break;
              
            case '❓ Помощь':
              const helpText = getHelpText();
              await sendTelegramMessage(chatId, helpText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлена помощь пользователю ${userId}`);
              break;
              
            case '💰 Доход':
              const incomeText = getIncomeText(userId);
              await sendTelegramMessage(chatId, incomeText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлена информация о доходе пользователю ${userId}`);
              break;
              
            case '⚙️ Настройки':
              const settingsText = getSettingsText();
              await sendTelegramMessage(chatId, settingsText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлены настройки пользователю ${userId}`);
              break;
              
            case '�� Обновить статус':
              const statusText = getStatusUpdateText();
              await sendTelegramMessage(chatId, statusText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлена информация об обновлении статуса пользователю ${userId}`);
              break;
              
            case '/start':
              const welcomeText = `
<b>👋 Добро пожаловать в DrillFlow Bot!</b>

Я помогу вам управлять заказами и отслеживать статус работы.

<i>Выберите действие из меню ниже:</i>
              `;
              
              await sendTelegramMessage(chatId, welcomeText, {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлено приветствие пользователю ${userId}`);
              break;
              
            default:
              await sendTelegramMessage(chatId, 'Выберите действие из меню:', {
                reply_markup: getMainMenuKeyboard()
              });
              console.log(`Отправлена подсказка пользователю ${userId}`);
              break;
          }
        } else if (update && update.callback_query) {
          // Обработка callback запросов (для inline клавиатуры)
          const callbackQuery = update.callback_query;
          const chatId = callbackQuery.message.chat.id;
          const userId = callbackQuery.from.id;
          const data = callbackQuery.data;
          
          // Обработка различных callback запросов
          if (data === 'pay_test_1') {
            await sendTelegramMessage(chatId, '<b>✅ Тестовый платеж выполнен успешно!</b>\n\nСпасибо за тестирование системы платежей.', {
              reply_markup: getMainMenuKeyboard()
            });
            console.log(`Выполнен тестовый платеж пользователем ${userId}`);
          } else if (data === 'back_to_main') {
            await sendTelegramMessage(chatId, 'Вы вернулись в главное меню', {
              reply_markup: getMainMenuKeyboard()
            });
            console.log(`Пользователь ${userId} вернулся в главное меню`);
          }
        }
        
        // Возвращаем успешный ответ
        res.status(200).send('OK');
      } catch (error) {
        console.error('Ошибка обработки вебхука:', error);
        res.status(500).send('Internal Server Error');
      }
    } else {
      // Метод не поддерживается
      res.status(405).send('Method Not Allowed');
    }
  }
}; 