const { PrismaClient } = require('@prisma/client');
const { mainKeyboard } = require('./index');

const prisma = new PrismaClient();

// Состояния редактирования профиля
const profileStates = new Map();

async function handleProfile(bot, msg, prisma, action = null) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      },
      include: {
        location: true,
        documents: true
      }
    });

    if (!user) {
      bot.sendMessage(chatId, 'Пожалуйста, сначала запустите бота командой /start');
      return;
    }

    if (action) {
      switch (action) {
        case '🔄 Обновить статус':
          return handleStatusUpdate(bot, chatId, user);
        case '💰 Доход':
          return handleIncome(bot, chatId, user);
        case '🔄 Подписка':
          return handleSubscription(bot, chatId, user);
        case '💳 Тестовый платеж':
          return handleTestPayment(bot, chatId, user);
      }
    }

    const state = profileStates.get(userId);
    if (state) {
      switch (state.field) {
        case 'name':
          await handleNameEdit(bot, msg, prisma, user);
          break;
        case 'phone':
          await handlePhoneEdit(bot, msg, prisma, user);
          break;
        case 'email':
          await handleEmailEdit(bot, msg, prisma, user);
          break;
        default:
          showProfile(bot, chatId, user);
      }
      return;
    }

    showProfile(bot, chatId, user);
  } catch (error) {
    console.error('Ошибка при обработке профиля:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при загрузке профиля. Пожалуйста, попробуйте позже.');
  }
}

function showProfile(bot, chatId, user) {
  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [{ text: '✏️ Изменить данные', callback_data: 'profile_edit' }],
        [{ text: '📄 Мои документы', callback_data: 'profile_documents' }],
        user.role === 'contractor' ? [{ text: '🔄 Обновить статус', callback_data: 'profile_status' }] : [],
        user.role === 'contractor' ? [{ text: '💰 Доход', callback_data: 'profile_income' }] : [],
        [{ text: '🔄 Подписка', callback_data: 'profile_subscription' }],
        [{ text: '💳 Тестовый платеж', callback_data: 'profile_payment' }],
        [{ text: '↩️ Назад', callback_data: 'back_to_menu' }]
      ].filter(row => row.length > 0)
    }
  };

  const documentsCount = user.documents?.length || 0;
  const verifiedDocuments = user.documents?.filter(doc => doc.status === 'verified').length || 0;

  const profileText = `
👤 *Профиль*

*Имя*: ${user.firstName || 'Не указано'}
*Фамилия*: ${user.lastName || 'Не указана'}
*Телефон*: ${user.phoneNumber || 'Не указан'}
*Роль*: ${user.role === 'contractor' ? 'Подрядчик' : 'Клиент'}
*Статус*: ${user.isActive ? '🟢 Активен' : '🔴 Неактивен'}

${user.role === 'contractor' ? `
📄 *Документы*: ${verifiedDocuments}/${documentsCount} проверено

📍 *Радиус работы*: ${user.location?.workRadius || 10} км` : ''}

*Уведомления*: ${user.notificationsEnabled ? '✅' : '❌'}
*Звук*: ${user.soundEnabled ? '✅' : '❌'}`;

  bot.sendMessage(chatId, profileText, {
    parse_mode: 'Markdown',
    ...keyboard
  });
}

async function handleProfileCallback(bot, query, prisma) {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;

  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      }
    });

    if (!user) {
      await bot.answerCallbackQuery(query.id, {
        text: 'Пользователь не найден',
        show_alert: true
      });
      return;
    }

    switch (data) {
      case 'profile_edit':
        const editKeyboard = {
          inline_keyboard: [
            [
              { text: '✏️ Имя', callback_data: 'profile_edit_name' },
              { text: '📱 Телефон', callback_data: 'profile_edit_phone' }
            ],
            [{ text: '📧 Email', callback_data: 'profile_edit_email' }],
            [{ text: '↩️ Назад', callback_data: 'back_to_profile' }]
          ]
        };
        await bot.editMessageText('Выберите, что хотите изменить:', {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: editKeyboard
        });
        break;

      case 'profile_edit_name':
        profileStates.set(userId, { field: 'name' });
        await bot.editMessageText('Введите новое имя:', {
          chat_id: chatId,
          message_id: query.message.message_id
        });
        break;

      case 'profile_edit_phone':
        profileStates.set(userId, { field: 'phone' });
        await bot.editMessageText('Введите новый номер телефона в формате +7XXXXXXXXXX:', {
          chat_id: chatId,
          message_id: query.message.message_id
        });
        break;

      case 'profile_edit_email':
        profileStates.set(userId, { field: 'email' });
        await bot.editMessageText('Введите новый email:', {
          chat_id: chatId,
          message_id: query.message.message_id
        });
        break;

      case 'back_to_profile':
        profileStates.delete(userId);
        showProfile(bot, chatId, user);
        break;

      case 'profile_documents':
        await handleDocuments(bot, query.message, prisma);
        break;

      case 'profile_status':
        await handleStatusUpdate(bot, chatId, user);
        break;

      case 'profile_income':
        await handleIncome(bot, chatId, user);
        break;

      case 'profile_subscription':
        await handleSubscription(bot, chatId, user);
        break;

      case 'profile_payment':
        await handleTestPayment(bot, chatId, user);
        break;

      case 'profile_status_active':
        await prisma.user.update({
          where: { id: user.id },
          data: { isActive: true }
        });

        // Отправляем уведомление через WebSocket
        broadcastEvent('USER_UPDATED', {
          id: user.id,
          isActive: true
        });

        await bot.editMessageText('✅ Ваш статус обновлен на "Активен"', {
          chat_id: chatId,
          message_id: query.message.message_id
        });
        break;

      case 'profile_status_inactive':
        await prisma.user.update({
          where: { id: user.id },
          data: { isActive: false }
        });

        // Отправляем уведомление через WebSocket
        broadcastEvent('USER_UPDATED', {
          id: user.id,
          isActive: false
        });

        await bot.editMessageText('🔴 Ваш статус обновлен на "Неактивен"', {
          chat_id: chatId,
          message_id: query.message.message_id
        });
        break;
    }

    await bot.answerCallbackQuery(query.id);
  } catch (error) {
    console.error('Ошибка при обработке callback профиля:', error);
    await bot.answerCallbackQuery(query.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

async function handleNameEdit(bot, msg, prisma, user) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const name = msg.text.trim();

  if (name.length < 2) {
    bot.sendMessage(chatId, 'Имя должно содержать минимум 2 символа. Попробуйте еще раз:');
    return;
  }

  try {
    await prisma.user.update({
      where: { id: user.id },
      data: { firstName: name }
    });

    profileStates.delete(userId);
    bot.sendMessage(chatId, '✅ Имя успешно обновлено!', mainKeyboard);
    showProfile(bot, chatId, { ...user, firstName: name });
  } catch (error) {
    console.error('Ошибка при обновлении имени:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при обновлении имени.');
  }
}

async function handlePhoneEdit(bot, msg, prisma, user) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const phone = msg.text.trim();

  const phoneRegex = /^\+7\d{10}$/;
  if (!phoneRegex.test(phone)) {
    bot.sendMessage(chatId, 'Неверный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX:');
    return;
  }

  try {
    await prisma.user.update({
      where: { id: user.id },
      data: { phoneNumber: phone }
    });

    profileStates.delete(userId);
    bot.sendMessage(chatId, '✅ Номер телефона успешно обновлен!', mainKeyboard);
    showProfile(bot, chatId, { ...user, phoneNumber: phone });
  } catch (error) {
    console.error('Ошибка при обновлении телефона:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при обновлении номера телефона.');
  }
}

async function handleEmailEdit(bot, msg, prisma, user) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const email = msg.text.trim().toLowerCase();

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    bot.sendMessage(chatId, 'Неверный формат email. Попробуйте еще раз:');
    return;
  }

  try {
    await prisma.user.update({
      where: { id: user.id },
      data: { email }
    });

    profileStates.delete(userId);
    bot.sendMessage(chatId, '✅ Email успешно обновлен!', mainKeyboard);
    showProfile(bot, chatId, { ...user, email });
  } catch (error) {
    console.error('Ошибка при обновлении email:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при обновлении email.');
  }
}

async function handleStatusUpdate(bot, chatId, user) {
  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [
          { text: '🟢 Активен', callback_data: 'profile_status_active' },
          { text: '🔴 Неактивен', callback_data: 'profile_status_inactive' }
        ],
        [{ text: '↩️ Назад', callback_data: 'back_to_profile' }]
      ]
    }
  };

  bot.sendMessage(chatId, 'Выберите ваш статус:', keyboard);
}

async function handleIncome(bot, chatId, user) {
  const incomeText = `
💰 *Статистика доходов*

За сегодня: 0₽
За неделю: 0₽
За месяц: 0₽
За все время: 0₽

_Функция находится в разработке_`;

  bot.sendMessage(chatId, incomeText, { parse_mode: 'Markdown' });
}

async function handleSubscription(bot, chatId, user) {
  const subscriptionText = `
🔄 *Подписка*

*Текущий план*: Базовый
*Статус*: Активна
*Действует до*: Бессрочно

_Функция находится в разработке_`;

  bot.sendMessage(chatId, subscriptionText, { parse_mode: 'Markdown' });
}

async function handleTestPayment(bot, chatId, user) {
  const paymentText = `
💳 *Тестовый платеж*

Для проверки работы платежной системы вы можете сделать тестовый платеж на сумму 1₽.
Средства будут возвращены автоматически.

_Функция находится в разработке_`;

  bot.sendMessage(chatId, paymentText, { parse_mode: 'Markdown' });
}

module.exports = {
  handleProfile,
  handleProfileCallback,
  profileStates
}; 