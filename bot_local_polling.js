// Локальный запуск Telegram бота в режиме long polling
// Гениальное решение для работы без публичного URL

const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// База данных пользователей (имитация)
const usersDB = {
  users: {},
  
  // Инициализация данных при первом запуске
  init() {
    // Попытка загрузить данные из файла, если он существует
    try {
      if (fs.existsSync('./users_data.json')) {
        const data = fs.readFileSync('./users_data.json', 'utf8');
        const loadedData = JSON.parse(data);
        this.users = loadedData;
        console.log('📂 База данных пользователей загружена успешно');
      }
    } catch (error) {
      console.error('❌ Ошибка при загрузке базы данных:', error);
    }
  },
  
  // Сохранение данных
  save() {
    try {
      fs.writeFileSync('./users_data.json', JSON.stringify(this.users, null, 2), 'utf8');
      console.log('💾 База данных пользователей сохранена');
    } catch (error) {
      console.error('❌ Ошибка при сохранении базы данных:', error);
    }
  },
  
  // Получение данных пользователя
  getUser(userId) {
    if (!this.users[userId]) {
      // Создание нового пользователя, если не существует
      const now = new Date();
      const registrationDate = `${now.getDate().toString().padStart(2, '0')}.${(now.getMonth() + 1).toString().padStart(2, '0')}.${now.getFullYear()}`;
      
      this.users[userId] = {
        id: userId,
        name: 'Новый пользователь',
        status: 'Активен',
        role: 'Подрядчик',
        rating: 5.0,
        completedOrders: 0,
        registrationDate: registrationDate,
        phone: '',
        email: '',
        address: '',
        notifications: {
          newOrders: true,
          messages: true,
          statusUpdates: true,
          financialOperations: true,
          emailNotifications: false
        },
        workZone: {
          radius: 50,
          center: 'Москва'
        },
        security: {
          twoFactorAuth: false,
          lastLogin: registrationDate
        },
        subscription: {
          status: 'Неактивна',
          plan: 'Базовый',
          activationDate: '',
          expirationDate: '',
          features: []
        },
        stats: {
          inProgress: 0,
          completed: 0,
          cancelled: 0,
          positiveReviews: 0,
          negativeReviews: 0,
          averageCompletionTime: 0,
          timelyCompletionRate: 0,
          workQuality: 'Новичок'
        },
        finance: {
          totalIncome: 0,
          averageCheck: 0,
          bonuses: 0,
          currentBalance: 0,
          pendingBalance: 0
        },
        orders: []
      };
      
      this.save();
    }
    
    return this.users[userId];
  },
  
  // Обновление данных пользователя
  updateUser(userId, userData) {
    this.users[userId] = { ...this.getUser(userId), ...userData };
    this.save();
    return this.users[userId];
  },
  
  // Обновление статуса пользователя
  updateUserStatus(userId, status) {
    const user = this.getUser(userId);
    user.status = status;
    this.save();
    return user;
  },
  
  // Добавление заказа пользователю
  addOrder(userId, orderData) {
    const user = this.getUser(userId);
    if (!user.orders) user.orders = [];
    user.orders.push(orderData);
    this.save();
    return user;
  }
};

// Инициализация базы данных при запуске
usersDB.init();

// Обработчик конкретных команд
const createCommandHandler = () => {
  // Получение основной клавиатуры
  function getMainMenuKeyboard() {
    return {
      keyboard: [
        [{ text: "📋 Профиль" }, { text: "📦 Заказы" }],
        [{ text: "🔍 Поиск заказов" }, { text: "🔄 Обновить статус" }],
        [{ text: "📊 Статистика" }, { text: "💰 Доход" }],
        [{ text: "⚙️ Настройки" }, { text: "🔄 Подписка" }],
        [{ text: "💳 Тестовый платеж" }, { text: "❓ Помощь" }]
      ],
      resize_keyboard: true
    };
  }

  // Получение текста профиля пользователя
  function getUserProfileText(userId) {
    const user = usersDB.getUser(userId);
    
    return `<b>📋 Профиль пользователя</b>

<b>ID:</b> ${user.id}
<b>Имя:</b> ${user.name}
<b>Статус:</b> ${user.status}
<b>Роль:</b> ${user.role}
<b>Рейтинг:</b> ${'⭐'.repeat(Math.round(user.rating))} (${user.rating.toFixed(1)})
<b>Выполнено заказов:</b> ${user.completedOrders}
<b>Регистрация:</b> ${user.registrationDate}

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
  function getOrdersText(userId) {
    const user = usersDB.getUser(userId);
    
    // Получаем активные и завершенные заказы
    const activeOrders = user.orders ? user.orders.filter(order => order.status === 'active') : [];
    const completedOrders = user.orders ? user.orders.filter(order => order.status === 'completed') : [];
    
    let ordersText = `<b>📦 Список заказов</b>\n\n`;
    
    if (activeOrders.length > 0) {
      ordersText += `<b>Активные заказы:</b>\n`;
      activeOrders.forEach(order => {
        ordersText += `• Заказ #${order.id} - ${order.title}, ${order.depth}м\n`;
        ordersText += `  📍 ${order.location}\n`;
        ordersText += `  💰 ${order.price.toLocaleString('ru-RU')} ₽\n`;
        ordersText += `  🕒 До: ${order.deadline}\n\n`;
      });
    } else {
      ordersText += `<b>Активные заказы:</b> нет активных заказов\n\n`;
    }
    
    if (completedOrders.length > 0) {
      ordersText += `<b>Завершенные заказы:</b>\n`;
      completedOrders.slice(0, 3).forEach(order => {
        ordersText += `• Заказ #${order.id} - ${order.title}, ${order.depth}м\n`;
        ordersText += `  ✅ Завершен ${order.completionDate}\n`;
        const stars = '⭐'.repeat(Math.round(order.rating));
        ordersText += `  ${stars} Оценка: ${order.rating.toFixed(1)}\n\n`;
      });
    } else {
      ordersText += `<b>Завершенные заказы:</b> нет завершенных заказов\n\n`;
    }
    
    // Если заказов вообще нет
    if (user.orders.length === 0) {
      ordersText += `У вас пока нет заказов. Используйте кнопку "Поиск заказов", чтобы найти подходящие предложения.\n`;
    }
    
    ordersText += `<i>Для получения деталей нажмите на номер заказа</i>`;
    
    return ordersText;
  }

  // Получение текста статистики
  function getStatisticsText(userId) {
    const user = usersDB.getUser(userId);
    const stats = user.stats;
    
    // Вычисляем общее количество заказов
    const totalOrders = stats.inProgress + stats.completed + stats.cancelled;
    
    // Рассчитываем процент положительных отзывов
    const totalReviews = stats.positiveReviews + stats.negativeReviews;
    const positivePercentage = totalReviews > 0 
      ? Math.round((stats.positiveReviews / totalReviews) * 100) 
      : 0;
    const negativePercentage = totalReviews > 0 
      ? Math.round((stats.negativeReviews / totalReviews) * 100) 
      : 0;
    
    // Форматируем текущее время для обновления данных
    const now = new Date();
    const updateTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    return `<b>📊 Статистика пользователя</b>

<b>Общая статистика:</b>
• Всего заказов: ${totalOrders}
• В работе: ${stats.inProgress}
• Завершено: ${stats.completed}
• Отменено: ${stats.cancelled}

<b>Рейтинг:</b> ${'⭐'.repeat(Math.round(user.rating))} (${user.rating.toFixed(1)})
<b>Положительных отзывов:</b> ${stats.positiveReviews} (${positivePercentage}%)
<b>Отрицательных отзывов:</b> ${stats.negativeReviews} (${negativePercentage}%)

<b>Производительность:</b>
• Среднее время выполнения: ${stats.averageCompletionTime} дня
• Соблюдение сроков: ${stats.timelyCompletionRate}%
• Качество работы: ${stats.workQuality}

<b>Финансы:</b>
• Общий доход: ${user.finance.totalIncome.toLocaleString('ru-RU')} ₽
• Средний чек: ${user.finance.averageCheck.toLocaleString('ru-RU')} ₽
• Бонусы: ${user.finance.bonuses.toLocaleString('ru-RU')} ₽

<i>Данные обновлены: сегодня в ${updateTime}</i>`;
  }

  // Получение информации о подписке
  function getSubscriptionText(userId) {
    const user = usersDB.getUser(userId);
    const subscription = user.subscription;
    
    // Проверяем, активна ли подписка
    let isActive = subscription.status === 'Активна';
    let expiration = subscription.expirationDate || '';
    let daysLeft = '';
    
    // Расчет оставшихся дней, если подписка активна
    if (isActive && subscription.expirationDate) {
      const now = new Date();
      const expDate = new Date(subscription.expirationDate.split('.').reverse().join('-'));
      const diffTime = Math.abs(expDate - now);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      daysLeft = ` (осталось ${diffDays} дней)`;
    }
    
    // Формирование текста в зависимости от статуса подписки
    let subsText = `<b>🔄 Подписка</b>\n\n`;
    
    if (isActive) {
      subsText += `<b>Текущий статус:</b> ${subscription.status} ✅\n`;
      subsText += `<b>Тариф:</b> ${subscription.plan}\n`;
      subsText += `<b>Дата активации:</b> ${subscription.activationDate}\n`;
      subsText += `<b>Действует до:</b> ${expiration}${daysLeft}\n\n`;
      
      subsText += `<b>Включено в тариф:</b>\n`;
      subscription.features.forEach(feature => {
        subsText += `• ${feature}\n`;
      });
      
      subsText += `\n<b>Стоимость продления:</b> 2,990 ₽/месяц\n\n`;
      subsText += `<i>Для продления подписки нажмите кнопку "Продлить"</i>`;
    } else {
      subsText += `<b>Текущий статус:</b> ${subscription.status} ❌\n\n`;
      subsText += `<b>Доступные тарифы:</b>\n`;
      subsText += `• Базовый - 990 ₽/месяц\n`;
      subsText += `• Стандартный - 1,990 ₽/месяц\n`;
      subsText += `• Премиум - 2,990 ₽/месяц\n\n`;
      subsText += `<i>Для активации подписки выберите тариф</i>`;
    }
    
    return subsText;
  }

  // Получение клавиатуры для подписки
  function getSubscriptionKeyboard(userId) {
    const user = usersDB.getUser(userId);
    
    if (user.subscription.status === 'Активна') {
      return {
        inline_keyboard: [
          [{ text: "🔄 Продлить подписку", callback_data: "subscription_extend" }],
          [{ text: "❌ Отменить подписку", callback_data: "subscription_cancel" }],
          [{ text: "🔙 Назад", callback_data: "back_to_main" }]
        ]
      };
    } else {
      return {
        inline_keyboard: [
          [{ text: "💰 Базовый (990 ₽)", callback_data: "subscription_basic" }],
          [{ text: "💰 Стандартный (1,990 ₽)", callback_data: "subscription_standard" }],
          [{ text: "💰 Премиум (2,990 ₽)", callback_data: "subscription_premium" }],
          [{ text: "🔙 Назад", callback_data: "back_to_main" }]
        ]
      };
    }
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
        [{ text: "💳 Оплатить 100 ₽", callback_data: "pay_test_100" }],
        [{ text: "💳 Оплатить 500 ₽", callback_data: "pay_test_500" }],
        [{ text: "💳 Оплатить 1000 ₽", callback_data: "pay_test_1000" }],
        [{ text: "🔙 Назад", callback_data: "back_to_main" }]
      ]
    };
  }

  // Получение информации о доходе
  function getIncomeText(userId) {
    const user = usersDB.getUser(userId);
    const finance = user.finance;
    
    // Получаем данные о доходах по месяцам
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();
    
    // Создаем месячные доходы, если их нет
    if (!finance.monthlyIncome) {
      finance.monthlyIncome = {};
    }
    
    // Форматирование названий месяцев
    const months = [
      'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
      'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    
    // Собираем статистику за последние 4 месяца
    let monthlyStats = '';
    let ordersCount = 0;
    
    for (let i = 0; i < 4; i++) {
      let monthIndex = currentMonth - i;
      let year = currentYear;
      
      if (monthIndex < 0) {
        monthIndex += 12;
        year -= 1;
      }
      
      const monthName = months[monthIndex];
      const monthKey = `${year}-${(monthIndex + 1).toString().padStart(2, '0')}`;
      const monthIncome = finance.monthlyIncome[monthKey] || 0;
      const monthOrders = finance.monthlyOrders ? (finance.monthlyOrders[monthKey] || 0) : 0;
      ordersCount += monthOrders;
      
      monthlyStats += `• ${monthName} ${year}: ${monthIncome.toLocaleString('ru-RU')} ₽ (${monthOrders} заказ${getOrdersEnding(monthOrders)})\n`;
    }
    
    return `<b>💰 Доход</b>

<b>Общий доход:</b> ${finance.totalIncome.toLocaleString('ru-RU')} ₽

<b>Статистика по месяцам:</b>
${monthlyStats}
<b>Текущий баланс:</b> ${finance.currentBalance.toLocaleString('ru-RU')} ₽
<b>Доступно к выводу:</b> ${finance.currentBalance.toLocaleString('ru-RU')} ₽
<b>В обработке:</b> ${finance.pendingBalance.toLocaleString('ru-RU')} ₽

<b>Способы вывода:</b>
• Банковская карта
• СБП
• Электронные кошельки

<i>Для вывода средств нажмите кнопку "Вывести"</i>`;
  }

  // Получение клавиатуры для дохода
  function getIncomeKeyboard() {
    return {
      inline_keyboard: [
        [{ text: "💸 Вывести средства", callback_data: "withdraw_funds" }],
        [{ text: "📊 Подробная статистика", callback_data: "income_stats" }],
        [{ text: "🔙 Назад", callback_data: "back_to_main" }]
      ]
    };
  }

  // Получение текста для поиска заказов
  function getOrderSearchText() {
    return `<b>🔍 Поиск заказов</b>

Выберите параметры поиска заказов:

• По местоположению
• По типу работ
• По стоимости
• По сроку выполнения

<i>Нажмите на соответствующую кнопку для начала поиска</i>`;
  }

  // Получение клавиатуры для поиска заказов
  function getOrderSearchKeyboard() {
    return {
      inline_keyboard: [
        [
          { text: "📍 По местоположению", callback_data: "search_location" },
          { text: "🔧 По типу работ", callback_data: "search_type" }
        ],
        [
          { text: "💰 По стоимости", callback_data: "search_price" },
          { text: "🕒 По сроку", callback_data: "search_deadline" }
        ],
        [
          { text: "🔄 Показать все заказы", callback_data: "search_all" }
        ],
        [
          { text: "🔙 Назад", callback_data: "back_to_main" }
        ]
      ]
    };
  }

  // Вспомогательная функция для правильных окончаний слова "заказ"
  function getOrdersEnding(count) {
    if (count % 10 === 1 && count % 100 !== 11) {
      return '';
    } else if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) {
      return 'а';
    } else {
      return 'ов';
    }
  }

  // Получение настроек
  function getSettingsText(userId) {
    const user = usersDB.getUser(userId);
    
    return `<b>⚙️ Настройки</b>

<b>Профиль:</b>
• Имя: ${user.name || 'Не указано'}
• Телефон: ${user.phone || 'Не указано'}
• Email: ${user.email || 'Не указано'}
• Адрес: ${user.address || 'Не указано'}

<b>Уведомления:</b>
• Новые заказы: ${user.notifications.newOrders ? '✅' : '❌'}
• Сообщения: ${user.notifications.messages ? '✅' : '❌'}
• Обновления статуса: ${user.notifications.statusUpdates ? '✅' : '❌'}
• Финансовые операции: ${user.notifications.financialOperations ? '✅' : '❌'}
• Email-уведомления: ${user.notifications.emailNotifications ? '✅' : '❌'}

<b>Рабочая зона:</b>
• Радиус: ${user.workZone.radius} км
• Центр: ${user.workZone.center}

<b>Безопасность:</b>
• Двухфакторная аутентификация: ${user.security.twoFactorAuth ? '✅' : '❌'}
• Последний вход: ${user.security.lastLogin}

<i>Для изменения настроек выберите соответствующий раздел</i>`;
  }

  // Получение клавиатуры для настроек
  function getSettingsKeyboard() {
    return {
      inline_keyboard: [
        [{ text: "👤 Редактировать профиль", callback_data: "settings_profile" }],
        [{ text: "🔔 Настройки уведомлений", callback_data: "settings_notifications" }],
        [{ text: "📍 Настройки рабочей зоны", callback_data: "settings_workzone" }],
        [{ text: "🔒 Безопасность", callback_data: "settings_security" }],
        [{ text: "🔙 Назад", callback_data: "back_to_main" }]
      ]
    };
  }

  // Получение клавиатуры для редактирования профиля
  function getProfileEditKeyboard() {
    return {
      inline_keyboard: [
        [{ text: "✏️ Изменить имя", callback_data: "edit_name" }],
        [{ text: "✏️ Изменить телефон", callback_data: "edit_phone" }],
        [{ text: "✏️ Изменить email", callback_data: "edit_email" }],
        [{ text: "✏️ Изменить адрес", callback_data: "edit_address" }],
        [{ text: "🔙 Назад к настройкам", callback_data: "back_to_settings" }]
      ]
    };
  }

  // Получение клавиатуры для настроек уведомлений
  function getNotificationsKeyboard(userId) {
    const user = usersDB.getUser(userId);
    const notifications = user.notifications;
    
    return {
      inline_keyboard: [
        [{ 
          text: `Новые заказы: ${notifications.newOrders ? '✅' : '❌'}`, 
          callback_data: "toggle_notification_newOrders" 
        }],
        [{ 
          text: `Сообщения: ${notifications.messages ? '✅' : '❌'}`, 
          callback_data: "toggle_notification_messages" 
        }],
        [{ 
          text: `Обновления статуса: ${notifications.statusUpdates ? '✅' : '❌'}`, 
          callback_data: "toggle_notification_statusUpdates" 
        }],
        [{ 
          text: `Финансовые операции: ${notifications.financialOperations ? '✅' : '❌'}`, 
          callback_data: "toggle_notification_financialOperations" 
        }],
        [{ 
          text: `Email-уведомления: ${notifications.emailNotifications ? '✅' : '❌'}`, 
          callback_data: "toggle_notification_emailNotifications" 
        }],
        [{ text: "🔙 Назад к настройкам", callback_data: "back_to_settings" }]
      ]
    };
  }

  // Получение клавиатуры для настроек рабочей зоны
  function getWorkZoneKeyboard() {
    return {
      inline_keyboard: [
        [{ text: "✏️ Изменить радиус", callback_data: "edit_radius" }],
        [{ text: "✏️ Изменить центр", callback_data: "edit_center" }],
        [{ text: "🔙 Назад к настройкам", callback_data: "back_to_settings" }]
      ]
    };
  }

  // Получение клавиатуры для настроек безопасности
  function getSecurityKeyboard(userId) {
    const user = usersDB.getUser(userId);
    
    return {
      inline_keyboard: [
        [{ 
          text: `Двухфакторная аутентификация: ${user.security.twoFactorAuth ? '✅' : '❌'}`, 
          callback_data: "toggle_2fa" 
        }],
        [{ text: "🔙 Назад к настройкам", callback_data: "back_to_settings" }]
      ]
    };
  }

  // Обработка обновления статуса
  function getStatusUpdateText(userId) {
    const user = usersDB.getUser(userId);
    
    return `<b>🔄 Обновление статуса</b>

Ваш текущий статус: <b>${user.status}</b>

<b>Доступные статусы:</b>
✅ <b>Свободен</b> - готов принимать заказы
⏳ <b>Занят</b> - выполняю заказ
🔄 <b>Перерыв</b> - временно недоступен
❌ <b>Недоступен</b> - не принимаю заказы

<i>Выберите статус, соответствующий вашей текущей ситуации</i>`;
  }

  // Получение клавиатуры выбора статуса
  function getStatusKeyboard() {
    return {
      inline_keyboard: [
        [
          { text: "✅ Свободен", callback_data: "status_free" },
          { text: "⏳ Занят", callback_data: "status_busy" }
        ],
        [
          { text: "🔄 Перерыв", callback_data: "status_break" },
          { text: "❌ Недоступен", callback_data: "status_unavailable" }
        ],
        [
          { text: "🔙 Назад", callback_data: "back_to_main" }
        ]
      ]
    };
  }

  return {
    getMainMenuKeyboard,
    getUserProfileText,
    getHelpText,
    getOrdersText,
    getStatisticsText,
    getSubscriptionText,
    getSubscriptionKeyboard,
    getTestPaymentText,
    getTestPaymentKeyboard,
    getIncomeText,
    getIncomeKeyboard,
    getOrderSearchText,
    getOrderSearchKeyboard,
    getSettingsText,
    getSettingsKeyboard,
    getProfileEditKeyboard,
    getNotificationsKeyboard,
    getWorkZoneKeyboard,
    getSecurityKeyboard,
    getStatusUpdateText,
    getStatusKeyboard
  };
};

// Токен из .env файла или жестко заданный
const TOKEN = process.env.TELEGRAM_TOKEN || "7293247588:AAH5qQkNUmhoTzZ-_MSw0gS4BKlSTAW5qdM";

// Проверка токена
if (!TOKEN || TOKEN.length < 20) {
  console.error('❌ ОШИБКА: Невалидный токен бота. Пожалуйста, укажите правильный токен в .env файле или в коде.');
  process.exit(1);
}

console.log('🔑 Инициализация бота с токеном:', TOKEN);

// Создаем экземпляр бота
const bot = new TelegramBot(TOKEN, { 
  polling: true,
  // Опции для отладки
  poll_options: {
    timeout: 60,
    limit: 100
  }
});

// Проверка соединения
bot.getMe()
  .then(botInfo => {
    console.log('✅ Бот успешно запущен и подключен к API Telegram');
    console.log(`📱 Имя бота: ${botInfo.first_name}`);
    console.log(`👤 Username: @${botInfo.username}`);
    console.log(`🆔 ID: ${botInfo.id}`);
  })
  .catch(error => {
    console.error('❌ Ошибка при подключении к API Telegram:', error.message);
    console.error('Проверьте корректность токена и доступ к api.telegram.org');
    process.exit(1);
  });

// Создаем обработчик команд
const handlers = createCommandHandler();

// Обработка начала работы с ботом
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const welcomeMessage = `<b>👋 Добро пожаловать в DrillFlow Bot!</b>

Это система управления буровыми работами.

Чем я могу помочь вам сегодня?`;

  bot.sendMessage(chatId, welcomeMessage, {
    parse_mode: 'HTML',
    reply_markup: handlers.getMainMenuKeyboard()
  });
});

// Обработка команды "📋 Профиль"
bot.onText(/📋 Профиль/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  bot.sendMessage(chatId, handlers.getUserProfileText(userId), {
    parse_mode: 'HTML',
    reply_markup: handlers.getMainMenuKeyboard()
  });
});

// Обработка команды "📦 Заказы"
bot.onText(/📦 Заказы/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  bot.sendMessage(chatId, handlers.getOrdersText(userId), {
    parse_mode: 'HTML',
    reply_markup: handlers.getMainMenuKeyboard()
  });
});

// Обработка команды "🔄 Обновить статус"
bot.onText(/🔄 Обновить статус/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  bot.sendMessage(chatId, handlers.getStatusUpdateText(userId), {
    parse_mode: 'HTML',
    reply_markup: handlers.getStatusKeyboard()
  });
});

// Обработка команды "📊 Статистика"
bot.onText(/📊 Статистика/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  bot.sendMessage(chatId, handlers.getStatisticsText(userId), {
    parse_mode: 'HTML',
    reply_markup: handlers.getMainMenuKeyboard()
  });
});

// Обработка команды "💰 Доход"
bot.onText(/💰 Доход/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  bot.sendMessage(chatId, handlers.getIncomeText(userId), {
    parse_mode: 'HTML',
    reply_markup: handlers.getIncomeKeyboard()
  });
});

// Обработка команды "⚙️ Настройки"
bot.onText(/⚙️ Настройки/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  bot.sendMessage(chatId, handlers.getSettingsText(userId), {
    parse_mode: 'HTML',
    reply_markup: handlers.getSettingsKeyboard()
  });
});

// Обработка команды "🔄 Подписка"
bot.onText(/🔄 Подписка/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  bot.sendMessage(chatId, handlers.getSubscriptionText(userId), {
    parse_mode: 'HTML',
    reply_markup: handlers.getSubscriptionKeyboard(userId)
  });
});

// Обработка команды "💳 Тестовый платеж"
bot.onText(/💳 Тестовый платеж/, (msg) => {
  const chatId = msg.chat.id;
  
  bot.sendMessage(chatId, handlers.getTestPaymentText(), {
    parse_mode: 'HTML',
    reply_markup: handlers.getTestPaymentKeyboard()
  });
});

// Обработка команды "❓ Помощь"
bot.onText(/❓ Помощь/, (msg) => {
  const chatId = msg.chat.id;
  
  bot.sendMessage(chatId, handlers.getHelpText(), {
    parse_mode: 'HTML',
    reply_markup: handlers.getMainMenuKeyboard()
  });
});

// Данные о текущих состояниях пользователей
const userStates = {};

// Обработка callback-запросов (инлайн-кнопки)
bot.on('callback_query', (callbackQuery) => {
  const chatId = callbackQuery.message.chat.id;
  const userId = callbackQuery.from.id;
  const data = callbackQuery.data;
  const messageId = callbackQuery.message.message_id;
  
  // Добавляем подробное логирование
  console.log('📢 Получен callback_query:');
  console.log('- chatId:', chatId);
  console.log('- userId:', userId);
  console.log('- data:', data);
  console.log('- messageId:', messageId);
  
  // Отвечаем на callback, чтобы убрать состояние загрузки с кнопки
  bot.answerCallbackQuery(callbackQuery.id)
    .then(() => console.log('✅ answerCallbackQuery успешно выполнен'))
    .catch(error => console.error('❌ Ошибка в answerCallbackQuery:', error));
  
  // Обрабатываем изменение статуса пользователя
  if (data.startsWith('status_')) {
    let newStatus = '';
    
    switch (data) {
      case 'status_free':
        newStatus = 'Свободен';
        break;
      case 'status_busy':
        newStatus = 'Занят';
        break;
      case 'status_break':
        newStatus = 'Перерыв';
        break;
      case 'status_unavailable':
        newStatus = 'Недоступен';
        break;
    }
    
    if (newStatus) {
      // Обновляем статус пользователя в базе данных
      usersDB.updateUserStatus(userId, newStatus);
      
      // Отправляем подтверждение
      bot.sendMessage(
        chatId,
        `<b>✅ Статус обновлен</b>\n\nВаш текущий статус: <b>${newStatus}</b>`,
        { 
          parse_mode: 'HTML',
          reply_markup: handlers.getMainMenuKeyboard() 
        }
      );
    }
  }
  // Обработка подписок
  else if (data.startsWith('subscription_')) {
    const user = usersDB.getUser(userId);
    
    if (data === 'subscription_extend') {
      // Продление текущей подписки
      const now = new Date();
      const expDate = new Date(now);
      expDate.setMonth(expDate.getMonth() + 1); // Продление на 1 месяц
      
      const formattedActivationDate = now.toLocaleDateString('ru-RU');
      const formattedExpirationDate = expDate.toLocaleDateString('ru-RU');
      
      user.subscription.activationDate = formattedActivationDate;
      user.subscription.expirationDate = formattedExpirationDate;
      
      usersDB.updateUser(userId, user);
      
      bot.sendMessage(
        chatId,
        `<b>✅ Подписка продлена!</b>\n\nВаша подписка "${user.subscription.plan}" активна до ${formattedExpirationDate}`,
        { 
          parse_mode: 'HTML',
          reply_markup: handlers.getMainMenuKeyboard() 
        }
      );
    } 
    else if (data === 'subscription_cancel') {
      // Отмена подписки
      user.subscription.status = 'Неактивна';
      usersDB.updateUser(userId, user);
      
      bot.sendMessage(
        chatId,
        `<b>❌ Подписка отменена</b>\n\nВаша подписка будет действовать до конца оплаченного периода, а затем автоматически отключится.`,
        { 
          parse_mode: 'HTML',
          reply_markup: handlers.getMainMenuKeyboard() 
        }
      );
    }
    else if (['subscription_basic', 'subscription_standard', 'subscription_premium'].includes(data)) {
      // Активация новой подписки
      const now = new Date();
      const expDate = new Date(now);
      expDate.setMonth(expDate.getMonth() + 1); // Подписка на 1 месяц
      
      const formattedActivationDate = now.toLocaleDateString('ru-RU');
      const formattedExpirationDate = expDate.toLocaleDateString('ru-RU');
      
      let planName = '';
      let planFeatures = [];
      
      if (data === 'subscription_basic') {
        planName = 'Базовый';
        planFeatures = [
          'Базовый доступ к заказам',
          'Стандартная статистика',
          'Лимит 5 заказов в день'
        ];
      } 
      else if (data === 'subscription_standard') {
        planName = 'Стандартный';
        planFeatures = [
          'Приоритетное получение заказов',
          'Расширенная статистика',
          'Лимит 10 заказов в день',
          'Техническая поддержка'
        ];
      } 
      else if (data === 'subscription_premium') {
        planName = 'Премиум';
        planFeatures = [
          'Приоритетное получение заказов',
          'Расширенная статистика',
          'Повышенный лимит заказов (до 15 в день)',
          'Персональный менеджер',
          'Бесплатные консультации'
        ];
      }
      
      user.subscription = {
        status: 'Активна',
        plan: planName,
        activationDate: formattedActivationDate,
        expirationDate: formattedExpirationDate,
        features: planFeatures
      };
      
      usersDB.updateUser(userId, user);
      
      bot.sendMessage(
        chatId,
        `<b>✅ Подписка активирована!</b>\n\nВаша подписка "${planName}" активна до ${formattedExpirationDate}`,
        { 
          parse_mode: 'HTML',
          reply_markup: handlers.getMainMenuKeyboard() 
        }
      );
    }
  }
  // Обработка настроек
  else if (data === 'settings_profile') {
    // Редактирование профиля
    bot.editMessageText(
      '<b>👤 Редактирование профиля</b>\n\nВыберите, что вы хотите изменить:',
      {
        chat_id: chatId,
        message_id: messageId,
        parse_mode: 'HTML',
        reply_markup: handlers.getProfileEditKeyboard()
      }
    );
  }
  else if (data === 'settings_notifications') {
    // Настройки уведомлений
    bot.editMessageText(
      '<b>🔔 Настройки уведомлений</b>\n\nВключите или отключите нужные уведомления:',
      {
        chat_id: chatId,
        message_id: messageId,
        parse_mode: 'HTML',
        reply_markup: handlers.getNotificationsKeyboard(userId)
      }
    );
  }
  else if (data === 'settings_workzone') {
    // Настройки рабочей зоны
    const user = usersDB.getUser(userId);
    
    bot.editMessageText(
      `<b>📍 Настройки рабочей зоны</b>

<b>Текущие настройки:</b>
• Радиус: ${user.workZone.radius} км
• Центр: ${user.workZone.center}

Выберите, что вы хотите изменить:`,
      {
        chat_id: chatId,
        message_id: messageId,
        parse_mode: 'HTML',
        reply_markup: handlers.getWorkZoneKeyboard()
      }
    );
  }
  else if (data === 'settings_security') {
    // Настройки безопасности
    bot.editMessageText(
      '<b>🔒 Настройки безопасности</b>\n\nУправление параметрами безопасности вашего аккаунта:',
      {
        chat_id: chatId,
        message_id: messageId,
        parse_mode: 'HTML',
        reply_markup: handlers.getSecurityKeyboard(userId)
      }
    );
  }
  else if (data === 'back_to_settings') {
    // Возврат к общим настройкам
    const userId = callbackQuery.from.id;
    
    bot.editMessageText(
      handlers.getSettingsText(userId),
      {
        chat_id: chatId,
        message_id: messageId,
        parse_mode: 'HTML',
        reply_markup: handlers.getSettingsKeyboard()
      }
    );
  }
  else if (data.startsWith('edit_')) {
    // Запрос на редактирование поля
    const fieldToEdit = data.replace('edit_', '');
    let promptText = '';
    
    switch (fieldToEdit) {
      case 'name':
        promptText = 'Введите ваше новое имя:';
        break;
      case 'phone':
        promptText = 'Введите ваш новый номер телефона:';
        break;
      case 'email':
        promptText = 'Введите ваш новый email:';
        break;
      case 'address':
        promptText = 'Введите ваш новый адрес:';
        break;
      case 'radius':
        promptText = 'Введите новый радиус рабочей зоны (в км):';
        break;
      case 'center':
        promptText = 'Введите новый центр рабочей зоны (город или адрес):';
        break;
    }
    
    if (promptText) {
      // Устанавливаем состояние пользователя
      userStates[userId] = { 
        action: 'edit',
        field: fieldToEdit,
        messageId: messageId
      };
      
      bot.sendMessage(chatId, promptText, {
        reply_markup: {
          force_reply: true
        }
      });
    }
  }
  else if (data.startsWith('toggle_notification_')) {
    // Переключение настройки уведомления
    const notificationType = data.replace('toggle_notification_', '');
    const user = usersDB.getUser(userId);
    
    // Инвертируем значение
    user.notifications[notificationType] = !user.notifications[notificationType];
    
    // Сохраняем изменения
    usersDB.updateUser(userId, user);
    
    // Обновляем отображение
    bot.editMessageReplyMarkup(
      handlers.getNotificationsKeyboard(userId).inline_keyboard,
      {
        chat_id: chatId,
        message_id: messageId
      }
    );
  }
  else if (data === 'toggle_2fa') {
    // Переключение двухфакторной аутентификации
    const user = usersDB.getUser(userId);
    
    // Инвертируем значение
    user.security.twoFactorAuth = !user.security.twoFactorAuth;
    
    // Сохраняем изменения
    usersDB.updateUser(userId, user);
    
    // Отправляем уведомление
    const status = user.security.twoFactorAuth ? 'включена' : 'отключена';
    
    bot.sendMessage(
      chatId,
      `<b>✅ Настройки обновлены</b>\n\nДвухфакторная аутентификация ${status}.`,
      { 
        parse_mode: 'HTML'
      }
    );
    
    // Обновляем отображение
    bot.editMessageReplyMarkup(
      handlers.getSecurityKeyboard(userId).inline_keyboard,
      {
        chat_id: chatId,
        message_id: messageId
      }
    );
  }
  // Обработка тестовых платежей
  else if (data.startsWith('pay_test_')) {
    const paymentAmount = data.replace('pay_test_', '');
    
    bot.sendMessage(
      chatId, 
      `<b>✅ Тестовый платеж на сумму ${paymentAmount} ₽ успешно выполнен</b>

Спасибо за тестирование системы оплаты!

Номер транзакции: TX-${Date.now().toString().slice(-8)}`,
      { 
        parse_mode: 'HTML',
        reply_markup: handlers.getMainMenuKeyboard()
      }
    );
  }
  // Обработка доходов и выплат
  else if (data === 'withdraw_funds') {
    // Запрос на вывод средств
    const user = usersDB.getUser(userId);
    
    if (user.finance.currentBalance <= 0) {
      // Если баланс пуст
      bot.sendMessage(
        chatId,
        `<b>❌ Недостаточно средств</b>\n\nНа вашем балансе нет доступных средств для вывода.`,
        { 
          parse_mode: 'HTML',
          reply_markup: handlers.getMainMenuKeyboard() 
        }
      );
    } else {
      // Если есть средства для вывода
      bot.sendMessage(
        chatId,
        `<b>💸 Вывод средств</b>\n\nВыберите способ вывода ${user.finance.currentBalance.toLocaleString('ru-RU')} ₽:`,
        { 
          parse_mode: 'HTML',
          reply_markup: {
            inline_keyboard: [
              [{ text: "💳 Банковская карта", callback_data: "withdraw_card" }],
              [{ text: "🏦 СБП", callback_data: "withdraw_sbp" }],
              [{ text: "💼 Электронный кошелек", callback_data: "withdraw_wallet" }],
              [{ text: "🔙 Назад", callback_data: "back_to_income" }]
            ]
          }
        }
      );
    }
  }
  else if (['withdraw_card', 'withdraw_sbp', 'withdraw_wallet'].includes(data)) {
    // Обработка конкретного метода вывода
    const user = usersDB.getUser(userId);
    const amount = user.finance.currentBalance;
    
    // Создаем транзакцию вывода
    const withdrawalId = 'W-' + Date.now().toString().slice(-8);
    
    // Обнуляем баланс и увеличиваем "в обработке"
    user.finance.pendingBalance += amount;
    user.finance.currentBalance = 0;
    
    // Сохраняем изменения
    usersDB.updateUser(userId, user);
    
    let method = '';
    if (data === 'withdraw_card') method = 'банковскую карту';
    else if (data === 'withdraw_sbp') method = 'СБП';
    else if (data === 'withdraw_wallet') method = 'электронный кошелек';
    
    bot.sendMessage(
      chatId,
      `<b>✅ Запрос на вывод средств принят</b>

<b>Сумма:</b> ${amount.toLocaleString('ru-RU')} ₽
<b>Метод:</b> ${method}
<b>ID транзакции:</b> ${withdrawalId}

Средства поступят на ваш счет в течение 24 часов. Статус транзакции можно отслеживать в разделе "Доход".`,
      { 
        parse_mode: 'HTML',
        reply_markup: handlers.getMainMenuKeyboard() 
      }
    );
  }
  else if (data === 'income_stats') {
    // Показать подробную статистику доходов
    const user = usersDB.getUser(userId);
    const completedOrders = user.orders ? user.orders.filter(o => o.status === 'completed') : [];
    
    // Вычисляем средний доход за заказ
    const avgOrderIncome = completedOrders.length > 0 
      ? user.finance.totalIncome / completedOrders.length 
      : 0;
    
    // Находим максимальный доход за заказ
    let maxOrderIncome = 0;
    let maxOrderId = '';
    
    completedOrders.forEach(order => {
      if (order.price > maxOrderIncome) {
        maxOrderIncome = order.price;
        maxOrderId = order.id;
      }
    });
    
    bot.sendMessage(
      chatId,
      `<b>📊 Подробная статистика доходов</b>

<b>Всего заработано:</b> ${user.finance.totalIncome.toLocaleString('ru-RU')} ₽
<b>Количество выполненных заказов:</b> ${completedOrders.length}
<b>Средний доход за заказ:</b> ${avgOrderIncome.toLocaleString('ru-RU')} ₽

<b>Самый выгодный заказ:</b> #${maxOrderId} - ${maxOrderIncome.toLocaleString('ru-RU')} ₽

<b>Прогноз на текущий месяц:</b> ${(avgOrderIncome * 4).toLocaleString('ru-RU')} ₽

<i>Данные обновляются автоматически при завершении заказов</i>`,
      { 
        parse_mode: 'HTML',
        reply_markup: {
          inline_keyboard: [
            [{ text: "🔙 Назад к доходам", callback_data: "back_to_income" }]
          ]
        }
      }
    );
  }
  else if (data === 'back_to_income') {
    // Возврат к экрану доходов
    bot.editMessageText(
      handlers.getIncomeText(userId),
      {
        chat_id: chatId,
        message_id: messageId,
        parse_mode: 'HTML',
        reply_markup: handlers.getIncomeKeyboard()
      }
    );
  }
  // Обработка поиска заказов
  else if (data.startsWith('search_')) {
    const searchType = data.replace('search_', '');
    
    if (searchType === 'all') {
      // Показать все доступные заказы
      // В реальном приложении здесь был бы API запрос к серверу
      
      // Генерируем несколько случайных заказов для демонстрации
      const availableOrders = [];
      
      for (let i = 0; i < 5; i++) {
        const orderId = Math.floor(2000 + Math.random() * 8000);
        const orderTypes = [
          'Бурение скважины',
          'Бурение на песок',
          'Ремонт скважины',
          'Чистка скважины',
          'Обслуживание насоса'
        ];
        const locations = [
          'Москва, ул. Ленина',
          'Санкт-Петербург, пр. Невский',
          'Казань, ул. Баумана',
          'Нижний Новгород, пл. Минина',
          'Екатеринбург, ул. Малышева'
        ];
        const randomType = orderTypes[Math.floor(Math.random() * orderTypes.length)];
        const randomLocation = locations[Math.floor(Math.random() * locations.length)];
        const randomDepth = Math.floor(10 + Math.random() * 40);
        const randomPrice = Math.floor(40000 + Math.random() * 100000);
        
        availableOrders.push({
          id: orderId,
          title: randomType,
          depth: randomDepth,
          location: randomLocation,
          price: randomPrice,
          deadline: '15.05.2024'
        });
      }
      
      // Формируем сообщение со списком заказов
      let ordersMessage = `<b>📦 Доступные заказы</b>\n\n`;
      
      availableOrders.forEach(order => {
        ordersMessage += `<b>Заказ #${order.id}</b> - ${order.title}, ${order.depth}м\n`;
        ordersMessage += `📍 ${order.location}\n`;
        ordersMessage += `💰 ${order.price.toLocaleString('ru-RU')} ₽\n`;
        ordersMessage += `🕒 Выполнить до: ${order.deadline}\n`;
        ordersMessage += `<i>Для принятия заказа нажмите кнопку ниже</i>\n\n`;
      });
      
      // Формируем клавиатуру для принятия заказов
      const inlineKeyboard = [];
      
      availableOrders.forEach(order => {
        inlineKeyboard.push([
          { text: `✅ Принять заказ #${order.id}`, callback_data: `accept_order_${order.id}` }
        ]);
      });
      
      inlineKeyboard.push([
        { text: "🔄 Показать все заказы", callback_data: "search_all" }
      ]);
      
      inlineKeyboard.push([
        { text: "🔙 Назад к поиску", callback_data: "back_to_search" }
      ]);
      
      bot.sendMessage(
        chatId,
        ordersMessage,
        { 
          parse_mode: 'HTML',
          reply_markup: {
            inline_keyboard: inlineKeyboard
          }
        }
      );
    } else {
      // Для других типов поиска (в реальном приложении здесь были бы фильтры)
      const searchMessages = {
        'location': 'Введите местоположение для поиска заказов:',
        'type': 'Выберите тип работ:',
        'price': 'Укажите диапазон стоимости (например, "50000-100000"):',
        'deadline': 'Укажите предпочтительный срок (например, "до 15.05.2024"):'
      };
      
      const promptText = searchMessages[searchType] || 'Уточните параметры поиска:';
      
      userStates[userId] = { 
        action: 'search',
        searchType: searchType
      };
      
      bot.sendMessage(
        chatId,
        `<b>🔍 Результаты поиска</b>\n\n${promptText}`,
        { 
          parse_mode: 'HTML',
          reply_markup: {
            force_reply: true
          }
        }
      );
    }
  }
  else if (data === 'back_to_search') {
    // Возврат к экрану поиска заказов
    bot.editMessageText(
      handlers.getOrderSearchText(),
      {
        chat_id: chatId,
        message_id: messageId,
        parse_mode: 'HTML',
        reply_markup: handlers.getOrderSearchKeyboard()
      }
    );
  }
  else if (data.startsWith('accept_order_')) {
    // Обработка принятия заказа
    const orderId = data.replace('accept_order_', '');
    
    // Генерируем заказ для пользователя
    const orderTypes = [
      'Бурение скважины',
      'Бурение на песок',
      'Ремонт скважины',
      'Чистка скважины',
      'Обслуживание насоса'
    ];
    const locations = [
      'Москва, ул. Ленина',
      'Санкт-Петербург, пр. Невский',
      'Казань, ул. Баумана',
      'Нижний Новгород, пл. Минина',
      'Екатеринбург, ул. Малышева'
    ];
    
    const randomType = orderTypes[Math.floor(Math.random() * orderTypes.length)];
    const randomLocation = locations[Math.floor(Math.random() * locations.length)];
    const randomDepth = Math.floor(10 + Math.random() * 40);
    const randomPrice = Math.floor(40000 + Math.random() * 100000);
    
    const newOrder = {
      id: orderId,
      title: randomType,
      depth: randomDepth,
      location: randomLocation,
      price: randomPrice,
      deadline: '15.05.2024',
      status: 'active',
      creationDate: new Date().toLocaleDateString('ru-RU')
    };
    
    // Добавляем заказ пользователю
    const user = usersDB.getUser(userId);
    
    // Обновляем статистику
    user.stats.inProgress += 1;
    
    // Добавляем заказ
    usersDB.addOrder(userId, newOrder);
    
    // Оповещаем пользователя
    bot.sendMessage(
      chatId,
      `<b>✅ Заказ #${orderId} принят!</b>

<b>Детали заказа:</b>
• Тип работ: ${newOrder.title}, ${newOrder.depth}м
• Адрес: ${newOrder.location}
• Стоимость: ${newOrder.price.toLocaleString('ru-RU')} ₽
• Срок выполнения: до ${newOrder.deadline}

<i>Для просмотра всех ваших заказов используйте команду "📦 Заказы"</i>`,
      { 
        parse_mode: 'HTML',
        reply_markup: handlers.getMainMenuKeyboard()
      }
    );
  }
  else if (data === 'back_to_main') {
    // Возврат в главное меню
    bot.sendMessage(
      chatId,
      '<b>🏠 Главное меню</b>\n\nВыберите нужный пункт меню:',
      { 
        parse_mode: 'HTML',
        reply_markup: handlers.getMainMenuKeyboard() 
      }
    );
  }
});

// Обработка всех текстовых сообщений (включая ответы на запросы)
bot.on('message', (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const text = msg.text;
  
  // Проверяем, находится ли пользователь в процессе поиска заказов
  if (userStates[userId] && userStates[userId].action === 'search') {
    const state = userStates[userId];
    const searchType = state.searchType;
    const searchQuery = text;
    
    // Очищаем состояние пользователя
    delete userStates[userId];
    
    // Формируем сообщение для пользователя
    let searchMessage = `<b>🔍 Результаты поиска</b>\n\n`;
    
    switch (searchType) {
      case 'location':
        searchMessage += `Заказы в регионе <b>${searchQuery}</b>:\n\n`;
        break;
      case 'type':
        searchMessage += `Заказы типа <b>${searchQuery}</b>:\n\n`;
        break;
      case 'price':
        searchMessage += `Заказы в ценовом диапазоне <b>${searchQuery}</b>:\n\n`;
        break;
      case 'deadline':
        searchMessage += `Заказы со сроком <b>${searchQuery}</b>:\n\n`;
        break;
    }
    
    // Генерируем случайные результаты поиска (от 0 до 3 заказов)
    const resultsCount = Math.floor(Math.random() * 4);
    
    if (resultsCount === 0) {
      searchMessage += "К сожалению, заказов по вашему запросу не найдено.\n\nПопробуйте изменить параметры поиска или посмотреть все доступные заказы.";
      
      bot.sendMessage(
        chatId,
        searchMessage,
        { 
          parse_mode: 'HTML',
          reply_markup: {
            inline_keyboard: [
              [{ text: "🔄 Показать все заказы", callback_data: "search_all" }],
              [{ text: "🔙 Назад к поиску", callback_data: "back_to_search" }]
            ]
          }
        }
      );
    } else {
      // Генерируем несколько заказов по запросу
      const availableOrders = [];
      
      for (let i = 0; i < resultsCount; i++) {
        const orderId = Math.floor(2000 + Math.random() * 8000);
        let orderType, orderLocation, orderPrice, orderDeadline;
        
        // Настраиваем заказы в зависимости от типа поиска
        if (searchType === 'location') {
          orderLocation = searchQuery;
        } else {
          const locations = [
            'Москва, ул. Ленина',
            'Санкт-Петербург, пр. Невский',
            'Казань, ул. Баумана',
            searchQuery // Добавляем искомое значение для правдоподобности
          ];
          orderLocation = locations[Math.floor(Math.random() * locations.length)];
        }
        
        if (searchType === 'type') {
          orderType = searchQuery;
        } else {
          const orderTypes = [
            'Бурение скважины',
            'Бурение на песок',
            'Ремонт скважины',
            searchQuery // Добавляем искомое значение для правдоподобности
          ];
          orderType = orderTypes[Math.floor(Math.random() * orderTypes.length)];
        }
        
        const randomDepth = Math.floor(10 + Math.random() * 40);
        
        if (searchType === 'price') {
          // Если поиск по цене, то пытаемся парсить диапазон
          const priceRange = searchQuery.split('-');
          if (priceRange.length === 2) {
            const minPrice = parseInt(priceRange[0]);
            const maxPrice = parseInt(priceRange[1]);
            
            if (!isNaN(minPrice) && !isNaN(maxPrice)) {
              orderPrice = Math.floor(minPrice + Math.random() * (maxPrice - minPrice));
            } else {
              orderPrice = Math.floor(40000 + Math.random() * 100000);
            }
          } else {
            // Если формат не распознан, используем случайную цену
            orderPrice = Math.floor(40000 + Math.random() * 100000);
          }
        } else {
          orderPrice = Math.floor(40000 + Math.random() * 100000);
        }
        
        if (searchType === 'deadline') {
          orderDeadline = searchQuery;
        } else {
          orderDeadline = '15.05.2024';
        }
        
        availableOrders.push({
          id: orderId,
          title: orderType,
          depth: randomDepth,
          location: orderLocation,
          price: orderPrice,
          deadline: orderDeadline
        });
      }
      
      // Формируем сообщение с результатами поиска
      availableOrders.forEach(order => {
        searchMessage += `<b>Заказ #${order.id}</b> - ${order.title}, ${order.depth}м\n`;
        searchMessage += `📍 ${order.location}\n`;
        searchMessage += `💰 ${order.price.toLocaleString('ru-RU')} ₽\n`;
        searchMessage += `🕒 Выполнить до: ${order.deadline}\n\n`;
      });
      
      // Формируем клавиатуру для принятия заказов
      const inlineKeyboard = [];
      
      availableOrders.forEach(order => {
        inlineKeyboard.push([
          { text: `✅ Принять заказ #${order.id}`, callback_data: `accept_order_${order.id}` }
        ]);
      });
      
      inlineKeyboard.push([
        { text: "🔄 Показать все заказы", callback_data: "search_all" }
      ]);
      
      inlineKeyboard.push([
        { text: "🔙 Назад к поиску", callback_data: "back_to_search" }
      ]);
      
      bot.sendMessage(
        chatId,
        searchMessage,
        { 
          parse_mode: 'HTML',
          reply_markup: {
            inline_keyboard: inlineKeyboard
          }
        }
      );
    }
    
    return; // Прерываем дальнейшую обработку
  }
  
  // Проверяем, находится ли пользователь в процессе редактирования настроек
  if (userStates[userId] && userStates[userId].action === 'edit') {
    const state = userStates[userId];
    const user = usersDB.getUser(userId);
    let success = false;
    
    // Обновляем соответствующее поле
    switch (state.field) {
      case 'name':
        user.name = text;
        success = true;
        break;
      case 'phone':
        user.phone = text;
        success = true;
        break;
      case 'email':
        user.email = text;
        success = true;
        break;
      case 'address':
        user.address = text;
        success = true;
        break;
      case 'radius':
        const radius = parseInt(text);
        if (!isNaN(radius) && radius > 0) {
          user.workZone.radius = radius;
          success = true;
        } else {
          bot.sendMessage(chatId, 'Пожалуйста, введите корректное число для радиуса.');
        }
        break;
      case 'center':
        user.workZone.center = text;
        success = true;
        break;
    }
    
    if (success) {
      // Сохраняем обновленные данные пользователя
      usersDB.updateUser(userId, user);
      
      // Отправляем подтверждение
      bot.sendMessage(
        chatId,
        `<b>✅ Настройки обновлены</b>\n\nЗначение успешно изменено.`,
        { 
          parse_mode: 'HTML',
          reply_markup: handlers.getMainMenuKeyboard()
        }
      );
      
      // Очищаем состояние пользователя
      delete userStates[userId];
    }
    
    return; // Прерываем дальнейшую обработку
  }
  
  // Если сообщение не обработано ни одним из регулярных выражений выше
  if (![
    '/start', '📋 Профиль', '📦 Заказы', '🔍 Поиск заказов', '🔄 Обновить статус', 
    '📊 Статистика', '💰 Доход', '⚙️ Настройки', '🔄 Подписка', 
    '💳 Тестовый платеж', '❓ Помощь'
  ].includes(text)) {
    bot.sendMessage(
      chatId,
      'Извините, я не понимаю эту команду. Пожалуйста, используйте меню или отправьте /help для получения списка доступных команд.',
      { reply_markup: handlers.getMainMenuKeyboard() }
    );
  }
});

// Обработка ошибок
bot.on('polling_error', (error) => {
  console.error('❌ Ошибка в работе бота (polling_error):', error.message);
  if (error.code) {
    console.error('Код ошибки:', error.code);
  }
  if (error.response && error.response.body) {
    console.error('Ответ API:', error.response.body);
  }
});

// Добавляем глобальный обработчик необработанных ошибок
process.on('uncaughtException', (error) => {
  console.error('❌ Необработанная ошибка:', error);
  console.error('Стек вызовов:', error.stack);
  // Не завершаем процесс, чтобы бот продолжал работу
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Необработанное отклонение промиса:', reason);
  // Не завершаем процесс, чтобы бот продолжал работу
});

// Добавляем команду для добавления тестового заказа (для демонстрации)
bot.onText(/\/add_test_order/, (msg) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  
  // Создаем тестовый заказ
  const orderId = Math.floor(1000 + Math.random() * 9000); // 4-значный ID
  const newOrder = {
    id: orderId,
    title: 'Бурение скважины',
    depth: Math.floor(15 + Math.random() * 25), // от 15 до 40 метров
    location: 'Москва, Ленинский пр-т',
    price: Math.floor(50000 + Math.random() * 50000), // от 50000 до 100000 рублей
    deadline: '25.04.2024',
    status: 'active',
    creationDate: new Date().toLocaleDateString('ru-RU')
  };
  
  // Добавляем заказ пользователю
  usersDB.addOrder(userId, newOrder);
  
  bot.sendMessage(chatId, `✅ Тестовый заказ #${orderId} добавлен успешно!`, {
    reply_markup: handlers.getMainMenuKeyboard()
  });
});

// Добавляем команду для завершения заказа (для демонстрации)
bot.onText(/\/complete_order (.+)/, (msg, match) => {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const orderId = match[1];
  
  // Получаем пользователя и его заказы
  const user = usersDB.getUser(userId);
  
  if (!user.orders) {
    bot.sendMessage(chatId, '❌ У вас нет активных заказов!', {
      reply_markup: handlers.getMainMenuKeyboard()
    });
    return;
  }
  
  // Ищем заказ по ID
  const orderIndex = user.orders.findIndex(o => o.id.toString() === orderId && o.status === 'active');
  
  if (orderIndex === -1) {
    bot.sendMessage(chatId, `❌ Заказ #${orderId} не найден или уже завершен!`, {
      reply_markup: handlers.getMainMenuKeyboard()
    });
    return;
  }
  
  // Обновляем заказ
  user.orders[orderIndex].status = 'completed';
  user.orders[orderIndex].completionDate = new Date().toLocaleDateString('ru-RU');
  user.orders[orderIndex].rating = 5.0; // Максимальный рейтинг для демонстрации
  
  // Обновляем статистику пользователя
  user.completedOrders += 1;
  user.stats.completed += 1;
  user.stats.inProgress -= 1;
  user.stats.positiveReviews += 1;
  
  // Обновляем финансы
  const orderPrice = user.orders[orderIndex].price;
  user.finance.totalIncome += orderPrice;
  user.finance.currentBalance += orderPrice;
  
  // Пересчитываем средний чек
  if (user.stats.completed > 0) {
    user.finance.averageCheck = user.finance.totalIncome / user.stats.completed;
  }
  
  // Сохраняем обновленные данные
  usersDB.updateUser(userId, user);
  
  bot.sendMessage(chatId, `✅ Заказ #${orderId} успешно завершен! Заработано: ${orderPrice.toLocaleString('ru-RU')} ₽`, {
    reply_markup: handlers.getMainMenuKeyboard()
  });
});

// Запускаем бота
console.log('🚀 Бот запущен в режиме локального polling!');
console.log('✅ Токен:', TOKEN);
console.log('💡 Для остановки бота нажмите Ctrl+C'); 