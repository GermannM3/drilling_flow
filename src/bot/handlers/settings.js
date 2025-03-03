const { getSettingsKeyboard } = require('../keyboards');

// Состояния настроек
const settingsStates = new Map();

// Обработчик настроек
async function handleSettings(bot, msg, prisma) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      }
    });

    if (!user) {
      bot.sendMessage(chatId, 'Пожалуйста, сначала запустите бота командой /start');
      return;
    }

    const keyboard = {
      reply_markup: {
        inline_keyboard: [
          [
            { text: user.notificationsEnabled ? '🔔 Уведомления Вкл' : '🔕 Уведомления Выкл', callback_data: 'settings_notifications' },
            { text: user.soundEnabled ? '🔊 Звук Вкл' : '🔇 Звук Выкл', callback_data: 'settings_sound' }
          ],
          user.role === 'contractor' ? [{ text: '📍 Радиус поиска', callback_data: 'settings_radius' }] : [],
          [{ text: '📱 Контактные данные', callback_data: 'settings_contacts' }],
          [{ text: '🔐 Конфиденциальность', callback_data: 'settings_privacy' }],
          [{ text: '↩️ Назад', callback_data: 'back_to_menu' }]
        ].filter(row => row.length > 0)
      }
    };

    const settingsText = `
⚙️ *Настройки*

*Уведомления*: ${user.notificationsEnabled ? '✅' : '❌'}
*Звук*: ${user.soundEnabled ? '✅' : '❌'}
${user.role === 'contractor' ? `*Радиус поиска*: ${user.location?.workRadius || 10} км` : ''}

_Выберите настройку для изменения_`;

    bot.sendMessage(chatId, settingsText, {
      parse_mode: 'Markdown',
      ...keyboard
    });
  } catch (error) {
    console.error('Ошибка при обработке настроек:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при загрузке настроек. Пожалуйста, попробуйте позже.');
  }
}

// Обработка callback-запросов настроек
async function handleSettingsCallback(bot, callbackQuery, prisma) {
  const chatId = callbackQuery.message.chat.id;
  const userId = callbackQuery.from.id;
  const data = callbackQuery.data;

  try {
    const user = await prisma.user.findUnique({
      where: { telegramId: BigInt(userId) },
      include: { contractor: true }
    });

    if (!user) {
      await bot.answerCallbackQuery(callbackQuery.id, {
        text: 'Пользователь не найден',
        show_alert: true
      });
      return;
    }

    switch (data) {
      case 'settings_notifications':
        settingsStates.set(userId, { setting: 'notifications' });
        await bot.editMessageText(
          'Управление уведомлениями\n\n' +
          'Отправьте "вкл" или "выкл" для управления уведомлениями.',
          {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id
          }
        );
        break;

      case 'settings_profile':
        // Перенаправляем на редактирование профиля
        await handleProfileSettings(bot, callbackQuery, user);
        break;

      case 'settings_location':
        // Запрашиваем геолокацию
        await handleLocationSettings(bot, callbackQuery);
        break;

      case 'settings_sound':
        settingsStates.set(userId, { setting: 'sound' });
        await bot.editMessageText(
          'Управление звуком\n\n' +
          'Отправьте "вкл" или "выкл" для управления звуковыми уведомлениями.',
          {
            chat_id: chatId,
            message_id: callbackQuery.message.message_id
          }
        );
        break;
    }

    await bot.answerCallbackQuery(callbackQuery.id);
  } catch (error) {
    console.error('Ошибка при обработке callback настроек:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Обработка настроек профиля
async function handleProfileSettings(bot, callbackQuery, user) {
  const chatId = callbackQuery.message.chat.id;

  const keyboard = {
    inline_keyboard: [
      [
        { text: "✏️ Изменить имя", callback_data: "profile_edit_name" },
        { text: "📱 Изменить телефон", callback_data: "profile_edit_phone" }
      ],
      [
        { text: "📧 Изменить email", callback_data: "profile_edit_email" }
      ],
      [
        { text: "↩️ Назад к настройкам", callback_data: "back_to_settings" }
      ]
    ]
  };

  await bot.editMessageText(
    '👤 Настройки профиля\n\n' +
    `Имя: ${user.name}\n` +
    `Телефон: ${user.phone || 'Не указан'}\n` +
    `Email: ${user.email || 'Не указан'}`,
    {
      chat_id: chatId,
      message_id: callbackQuery.message.message_id,
      reply_markup: keyboard
    }
  );
}

// Обработка настроек геолокации
async function handleLocationSettings(bot, callbackQuery) {
  const chatId = callbackQuery.message.chat.id;

  const keyboard = {
    keyboard: [
      [{
        text: '📍 Отправить геолокацию',
        request_location: true
      }]
    ],
    resize_keyboard: true,
    one_time_keyboard: true
  };

  await bot.editMessageText(
    '📍 Настройки геолокации\n\n' +
    'Отправьте свою геолокацию для обновления местоположения.',
    {
      chat_id: chatId,
      message_id: callbackQuery.message.message_id
    }
  );

  await bot.sendMessage(chatId,
    'Используйте кнопку ниже для отправки геолокации:',
    { reply_markup: keyboard }
  );
}

module.exports = {
  handleSettings,
  handleSettingsCallback,
  settingsStates
}; 