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
    const req = https.request(
      apiUrl,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': data.length
        }
      },
      (res) => {
        let responseData = '';
        
        res.on('data', (chunk) => {
          responseData += chunk;
        });
        
        res.on('end', () => {
          try {
            const parsedData = JSON.parse(responseData);
            resolve(parsedData);
          } catch (e) {
            reject(new Error(`Failed to parse Telegram API response: ${e.message}`));
          }
        });
      }
    );
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.write(data);
    req.end();
  });
}

// Получение основной клавиатуры
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

// Получение текста профиля пользователя
function getUserProfileText(userId) {
  return `<b>📋 Профиль пользователя</b>

<b>ID:</b> ${userId}
<b>Имя:</b> Тестовый пользователь
<b>Статус:</b> Активен
<b>Роль:</b> Подрядчик
<b>Рейтинг:</b> ⭐⭐⭐⭐⭐ (5.0)
<b>Выполнено заказов:</b> 42
<b>Регистрация:</b> 15.01.2024

<i>Для редактирования профиля используйте меню настроек</i>`;
}

// Получение текста справки
function getHelpText() {
  return `<b>❓ Помощь и информация</b>

<b>DrillFlow Bot</b> - система для управления буровыми работами.

<b>Доступные команды:</b>
• /start - Перезапуск бота
• 📋 Профиль - Ваш профиль
• 📦 Заказы - Доступные и текущие заказы
• 🔄 Обновить статус - Изменить ваш статус
• 📊 Статистика - Ваша статистика
• 💰 Доход - Финансовая информация
• ⚙️ Настройки - Настройки профиля
• 🔄 Подписка - Управление подпиской
• 💳 Тестовый платеж - Тестирование оплаты
• ❓ Помощь - Эта справка

<b>Поддержка:</b>
По вопросам работы бота обращайтесь в службу поддержки: @DrillFlow_Support`;
}

// Получение текста со списком заказов
function getOrdersText() {
  return `<b>📦 Список заказов</b>

<b>Активные заказы:</b>
• Заказ #1587 - Бурение скважины, 25м
  📍 Москва, Ленинский пр-т
  💰 65,000 ₽
  🕒 До: 25.03.2024

<b>Завершенные заказы:</b>
• Заказ #1498 - Бурение на песок, 15m
  ✅ Завершен 15.03.2024
  ⭐⭐⭐⭐⭐ Оценка: 5.0

<i>Для получения деталей нажмите на номер заказа</i>`;
}

// Получение текста статистики
function getStatisticsText(userId) {
  return `<b>📊 Статистика пользователя</b>

<b>Общая статистика:</b>
• Всего заказов: 42
• В работе: 1
• Завершено: 41
• Отменено: 0

<b>Рейтинг:</b> ⭐⭐⭐⭐⭐ (5.0)
<b>Положительных отзывов:</b> 41 (100%)
<b>Отрицательных отзывов:</b> 0 (0%)

<b>Производительность:</b>
• Среднее время выполнения: 2.5 дня
• Соблюдение сроков: 98%
• Качество работы: Высокое

<b>Финансы:</b>
• Общий доход: 2,738,500 ₽
• Средний чек: 65,202 ₽
• Бонусы: 12,500 ₽

<i>Данные обновлены: сегодня в 12:45</i>`;
}

// Получение информации о подписке
function getSubscriptionText() {
  return `<b>🔄 Подписка</b>

<b>Текущий статус:</b> Активна ✅
<b>Тариф:</b> Премиум
<b>Дата активации:</b> 01.02.2024
<b>Действует до:</b> 01.04.2024 (осталось 15 дней)

<b>Включено в тариф:</b>
• Приоритетное получение заказов
• Расширенная статистика
• Повышенный лимит заказов (до 15 в день)
• Персональный менеджер
• Бесплатные консультации

<b>Стоимость продления:</b> 2,990 ₽/месяц

<i>Для продления подписки нажмите кнопку "Продлить"</i>`;
}

// Получение информации о тестовом платеже
function getTestPaymentText() {
  return `<b>💳 Тестовый платеж</b>

Вы можете протестировать систему платежей на примере тестового платежа.

<b>Сумма:</b> 100 ₽
<b>Назначение:</b> Тестирование системы оплаты
<b>Метод:</b> Банковская карта

<i>Это тестовый платеж, реальные деньги не будут списаны</i>`;
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

// Получение информации о доходе
function getIncomeText(userId) {
  return `<b>💰 Доход</b>

<b>Общий доход:</b> 2,738,500 ₽

<b>Статистика по месяцам:</b>
• Март 2024: 258,500 ₽ (4 заказа)
• Февраль 2024: 487,000 ₽ (7 заказов)
• Январь 2024: 532,000 ₽ (8 заказов)
• Декабрь 2023: 665,000 ₽ (10 заказов)

<b>Текущий баланс:</b> 156,500 ₽
<b>Доступно к выводу:</b> 156,500 ₽
<b>В обработке:</b> 0 ₽

<b>Способы вывода:</b>
• Банковская карта
• СБП
• Электронные кошельки

<i>Для вывода средств нажмите кнопку "Вывести"</i>`;
}

// Получение настроек
function getSettingsText() {
  return `<b>⚙️ Настройки</b>

<b>Профиль:</b>
• Имя: Тестовый пользователь
• Телефон: +7 (999) 123-45-67
• Email: user@example.com
• Адрес: Москва, ул. Примерная, д. 123

<b>Уведомления:</b>
• Новые заказы: ✅
• Сообщения: ✅
• Обновления статуса: ✅
• Финансовые операции: ✅
• Email-уведомления: ❌

<b>Рабочая зона:</b>
• Радиус: 50 км
• Центр: Москва

<b>Безопасность:</b>
• Двухфакторная аутентификация: ❌
• Последний вход: 22.03.2024, 14:30

<i>Для изменения настроек выберите соответствующий раздел</i>`;
}

// Обработка обновления статуса
function getStatusUpdateText() {
  return `<b>🔄 Обновление статуса</b>

Ваш текущий статус: <b>Свободен</b>

<b>Доступные статусы:</b>
✅ <b>Свободен</b> - готов принимать заказы
⏳ <b>Занят</b> - выполняю заказ
🔄 <b>Перерыв</b> - временно недоступен
❌ <b>Недоступен</b> - не принимаю заказы

<i>Выберите статус, соответствующий вашей текущей ситуации</i>`;
}

// Основной обработчик
async function handler(req, res) {
  if (req.method === 'GET') {
    // Обработка GET-запроса (для проверки вебхука)
    const response = {
      app: "DrillFlow Bot",
      version: "1.0.0",
      status: "running",
      webhook_url: "https://drilling-flow.vercel.app/api/telegram_webhook_handler",
      telegram_bot: "@Drill_Flow_bot",
      updated_at: new Date().toISOString(),
      version_tag: "v2023-10-21-04",
      handler_file: "telegram_webhook_handler.js"
    };
    
    res.status(200).json(response);
  } else if (req.method === 'POST') {
    // Обработка POST-запроса от Telegram
    try {
      const update = req.body;
      console.log('Received update:', JSON.stringify(update, null, 2));
      
      // Обработка callback запросов (инлайн кнопки)
      if (update && update.callback_query) {
        const callbackQuery = update.callback_query;
        const data = callbackQuery.data;
        const chatId = callbackQuery.message.chat.id;
        
        // Обработка различных callback-данных
        if (data === 'pay_test_1') {
          // Обработка тестового платежа
          await sendTelegramMessage(
            chatId, 
            '<b>✅ Тестовый платеж успешно выполнен</b>\n\nСпасибо за тестирование системы оплаты!'
          );
        } else if (data === 'back_to_main') {
          // Возврат в главное меню
          await sendTelegramMessage(
            chatId,
            '<b>🏠 Главное меню</b>\n\nВыберите нужный пункт меню:',
            { reply_markup: getMainMenuKeyboard() }
          );
        }
        
        // Отвечаем на callback, чтобы убрать состояние загрузки с кнопки
        res.status(200).json({
          method: 'answerCallbackQuery',
          callback_query_id: callbackQuery.id
        });
        return;
      }
      
      // Обработка обычных сообщений
      if (update && update.message) {
        const message = update.message;
        const chatId = message.chat.id;
        const text = message.text || '';
        const userId = message.from.id;
        
        // Обработка различных команд и сообщений
        if (text === '/start') {
          // Команда /start
          const welcomeMessage = `<b>👋 Добро пожаловать в DrillFlow Bot!</b>

Это система управления буровыми работами.

Чем я могу помочь вам сегодня?`;
          
          await sendTelegramMessage(chatId, welcomeMessage, {
            reply_markup: getMainMenuKeyboard()
          });
        } else {
          // Обработка других команд с клавиатуры
          switch (text) {
            case '📋 Профиль':
              const profileText = getUserProfileText(userId);
              await sendTelegramMessage(chatId, profileText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            case '📦 Заказы':
              const ordersText = getOrdersText();
              await sendTelegramMessage(chatId, ordersText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            case '🔄 Обновить статус':
              const statusText = getStatusUpdateText();
              await sendTelegramMessage(chatId, statusText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            case '📊 Статистика':
              const statsText = getStatisticsText(userId);
              await sendTelegramMessage(chatId, statsText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            case '💰 Доход':
              const incomeText = getIncomeText(userId);
              await sendTelegramMessage(chatId, incomeText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            case '⚙️ Настройки':
              const settingsText = getSettingsText();
              await sendTelegramMessage(chatId, settingsText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            case '🔄 Подписка':
              const subscriptionText = getSubscriptionText();
              await sendTelegramMessage(chatId, subscriptionText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            case '💳 Тестовый платеж':
              const paymentText = getTestPaymentText();
              await sendTelegramMessage(chatId, paymentText, {
                reply_markup: getTestPaymentKeyboard()
              });
              break;
              
            case '❓ Помощь':
              const helpText = getHelpText();
              await sendTelegramMessage(chatId, helpText, {
                reply_markup: getMainMenuKeyboard()
              });
              break;
              
            default:
              // Неизвестная команда или обычное сообщение
              await sendTelegramMessage(
                chatId,
                'Извините, я не понимаю эту команду. Пожалуйста, используйте меню или отправьте /help для получения списка доступных команд.',
                { reply_markup: getMainMenuKeyboard() }
              );
          }
        }
      }
      
      res.status(200).json({ ok: true });
    } catch (error) {
      console.error('Error handling webhook:', error);
      res.status(500).json({ 
        error: 'Internal Server Error',
        message: error.message
      });
    }
  } else {
    // Метод не поддерживается
    res.setHeader('Allow', ['GET', 'POST']);
    res.status(405).json({ error: `Method ${req.method} not allowed` });
  }
}

// Экспортируем обработчик в формате CommonJS
module.exports = {
  default: handler
}; 