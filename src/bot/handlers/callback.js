const { registrationStates } = require('./registration');
const { getMainMenuKeyboard } = require('../keyboards');
const { getUserProfileText } = require('../utils');

async function handleCallback(bot, callbackQuery, prisma) {
  const chatId = callbackQuery.message.chat.id;
  const userId = callbackQuery.from.id;
  const data = callbackQuery.data;

  try {
    // Проверяем, существует ли пользователь
    const user = await prisma.user.findUnique({
      where: { telegramId: BigInt(userId) },
      include: { contractor: true }
    });

    // Обработка регистрации
    if (data.startsWith('register_')) {
      await handleRegistrationCallback(bot, callbackQuery, prisma);
      return;
    }

    // Если пользователь не зарегистрирован
    if (!user) {
      await bot.answerCallbackQuery(callbackQuery.id, {
        text: 'Пожалуйста, сначала зарегистрируйтесь',
        show_alert: true
      });
      return;
    }

    // Обработка различных типов callback-запросов
    if (data.startsWith('order_')) {
      await handleOrderCallback(bot, callbackQuery, prisma, user);
    } else if (data.startsWith('profile_')) {
      await handleProfileCallback(bot, callbackQuery, prisma, user);
    } else if (data.startsWith('settings_')) {
      await handleSettingsCallback(bot, callbackQuery, prisma, user);
    } else if (data.startsWith('admin_') && user.role === 'ADMIN') {
      await handleAdminCallback(bot, callbackQuery, prisma, user);
    } else if (data === 'back_to_menu') {
      await handleBackToMenu(bot, callbackQuery, user);
    } else {
      await bot.answerCallbackQuery(callbackQuery.id, {
        text: 'Неизвестная команда',
        show_alert: true
      });
    }
  } catch (error) {
    console.error('Ошибка при обработке callback:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Обработка callback-запросов регистрации
async function handleRegistrationCallback(bot, callbackQuery, prisma) {
  const chatId = callbackQuery.message.chat.id;
  const userId = callbackQuery.from.id;
  const data = callbackQuery.data;

  // Проверяем, не зарегистрирован ли уже пользователь
  const existingUser = await prisma.user.findUnique({
    where: { telegramId: BigInt(userId) }
  });

  if (existingUser) {
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Вы уже зарегистрированы!',
      show_alert: true
    });
    return;
  }

  if (data === 'register_client' || data === 'register_contractor') {
    // Начинаем процесс регистрации
    registrationStates.set(userId, {
      step: 'AWAITING_NAME',
      role: data === 'register_contractor' ? 'CONTRACTOR' : 'CLIENT'
    });

    await bot.editMessageText(
      'Пожалуйста, введите ваше имя:',
      {
        chat_id: chatId,
        message_id: callbackQuery.message.message_id
      }
    );
  }

  await bot.answerCallbackQuery(callbackQuery.id);
}

// Обработка callback-запросов заказов
async function handleOrderCallback(bot, callbackQuery, prisma, user) {
  const chatId = callbackQuery.message.chat.id;
  const data = callbackQuery.data;
  const orderId = data.split('_')[2]; // order_action_id

  try {
    if (data.startsWith('order_accept_')) {
      // Принятие заказа подрядчиком
      await handleOrderAccept(bot, callbackQuery, prisma, user, orderId);
    } else if (data.startsWith('order_reject_')) {
      // Отклонение заказа подрядчиком
      await handleOrderReject(bot, callbackQuery, prisma, user, orderId);
    } else if (data.startsWith('order_cancel_')) {
      // Отмена заказа клиентом
      await handleOrderCancel(bot, callbackQuery, prisma, user, orderId);
    } else if (data.startsWith('order_complete_')) {
      // Завершение заказа подрядчиком
      await handleOrderComplete(bot, callbackQuery, prisma, user, orderId);
    } else if (data.startsWith('order_details_')) {
      // Просмотр деталей заказа
      await handleOrderDetails(bot, callbackQuery, prisma, user, orderId);
    }
  } catch (error) {
    console.error('Ошибка при обработке заказа:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Обработка callback-запросов профиля
async function handleProfileCallback(bot, callbackQuery, prisma, user) {
  const chatId = callbackQuery.message.chat.id;
  const data = callbackQuery.data;

  try {
    if (data === 'profile') {
      // Показываем профиль пользователя
      const profileText = await getUserProfileText(user);
      await bot.editMessageText(profileText, {
        chat_id: chatId,
        message_id: callbackQuery.message.message_id,
        parse_mode: 'HTML',
        reply_markup: await getMainMenuKeyboard(user.role)
      });
    }
  } catch (error) {
    console.error('Ошибка при обработке профиля:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Обработка callback-запросов настроек
async function handleSettingsCallback(bot, callbackQuery, prisma, user) {
  const chatId = callbackQuery.message.chat.id;
  const data = callbackQuery.data;

  try {
    // Обработка различных настроек
    switch (data) {
      case 'settings_notifications':
        // Настройки уведомлений
        break;
      case 'settings_profile':
        // Настройки профиля
        break;
      case 'settings_location':
        // Настройки геолокации
        break;
      case 'settings_sound':
        // Настройки звука
        break;
    }
  } catch (error) {
    console.error('Ошибка при обработке настроек:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Обработка callback-запросов администратора
async function handleAdminCallback(bot, callbackQuery, prisma, user) {
  const chatId = callbackQuery.message.chat.id;
  const data = callbackQuery.data;

  try {
    if (data.startsWith('admin_approve_')) {
      // Одобрение подрядчика
      const contractorId = data.split('_')[2];
      await handleContractorApproval(bot, callbackQuery, prisma, contractorId);
    } else if (data.startsWith('admin_reject_')) {
      // Отклонение подрядчика
      const contractorId = data.split('_')[2];
      await handleContractorRejection(bot, callbackQuery, prisma, contractorId);
    } else if (data === 'admin_stats') {
      // Показ статистики
      await handleAdminStats(bot, callbackQuery, prisma);
    }
  } catch (error) {
    console.error('Ошибка при обработке админ-команды:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Возврат в главное меню
async function handleBackToMenu(bot, callbackQuery, user) {
  const chatId = callbackQuery.message.chat.id;

  try {
    await bot.editMessageText(
      'Главное меню',
      {
        chat_id: chatId,
        message_id: callbackQuery.message.message_id,
        reply_markup: await getMainMenuKeyboard(user.role)
      }
    );
    await bot.answerCallbackQuery(callbackQuery.id);
  } catch (error) {
    console.error('Ошибка при возврате в меню:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

module.exports = { handleCallback }; 