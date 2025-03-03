const { PrismaClient } = require('@prisma/client');
const { mainKeyboard } = require('./index');
const { Markup } = require('telegraf');

const prisma = new PrismaClient();

// Состояния редактирования профиля
const profileStates = new Map();

async function handleProfile(ctx) {
  try {
    const user = await ctx.prisma.user.findFirst({
      where: {
        telegramId: BigInt(ctx.from.id)
      },
      include: {
        subscription: true,
        settings: true
      }
    });

    if (!user) {
      return ctx.reply('Пользователь не найден. Используйте /start для регистрации.');
    }

    await showProfile(ctx, user);
  } catch (error) {
    console.error('Ошибка при обработке профиля:', error);
    ctx.reply('Произошла ошибка при загрузке профиля. Попробуйте позже.');
  }
}

async function showProfile(ctx, user) {
  const subscriptionStatus = user.subscription 
    ? `${user.subscription.type} (до ${new Date(user.subscription.endDate).toLocaleDateString()})`
    : 'Не активна';

  const keyboard = Markup.inlineKeyboard([
    [
      Markup.button.callback('✏️ Редактировать', 'profile_edit'),
      Markup.button.callback('⚙️ Настройки', 'profile_settings')
    ],
    [
      Markup.button.callback('📄 Документы', 'profile_documents'),
      Markup.button.callback('🔄 Статус', 'profile_status')
    ],
    [
      Markup.button.callback('💰 Доход', 'profile_income'),
      Markup.button.callback('🔔 Подписка', 'profile_subscription')
    ],
    [Markup.button.callback('💳 Тестовый платеж', 'profile_payment')]
  ]);

  const message = `
👤 <b>Ваш профиль</b>

🆔 ID: ${user.telegramId}
👤 Имя: ${user.firstName} ${user.lastName || ''}
📱 Телефон: ${user.phoneNumber || 'Не указан'}
📧 Email: ${user.email || 'Не указан'}
👔 Роль: ${user.role}
🔄 Статус: ${user.isActive ? '🟢 Активен' : '🔴 Неактивен'}
💫 Подписка: ${subscriptionStatus}

⚙️ Настройки:
🔔 Уведомления: ${user.settings?.notifications ? 'Включены' : 'Выключены'}
🌍 Язык: ${user.settings?.language || 'Русский'}
📍 Радиус поиска: ${user.settings?.radius || 50} км
`;

  await ctx.replyWithHTML(message, keyboard);
}

async function handleProfileCallback(bot, query, prisma) {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;

  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      },
      include: {
        subscription: true,
        settings: true
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
        const editKeyboard = Markup.inlineKeyboard([
          [
            Markup.button.callback('✏️ Имя', 'profile_edit_name'),
            Markup.button.callback('📱 Телефон', 'profile_edit_phone')
          ],
          [
            Markup.button.callback('📧 Email', 'profile_edit_email'),
            Markup.button.callback('🌍 Язык', 'profile_edit_language')
          ],
          [Markup.button.callback('↩️ Назад', 'back_to_profile')]
        ]);
        await bot.editMessageText('Выберите, что хотите изменить:', {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: editKeyboard
        });
        break;

      case 'profile_settings':
        const settingsKeyboard = Markup.inlineKeyboard([
          [
            Markup.button.callback('🔔 Уведомления', 'settings_notifications'),
            Markup.button.callback('📍 Радиус', 'settings_radius')
          ],
          [Markup.button.callback('↩️ Назад', 'back_to_profile')]
        ]);
        await bot.editMessageText('Настройки профиля:', {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: settingsKeyboard
        });
        break;

      case 'profile_subscription':
        const subKeyboard = Markup.inlineKeyboard([
          [Markup.button.callback('💎 Премиум - 999₽/мес', 'sub_premium')],
          [Markup.button.callback('🚀 Профессионал - 1999₽/мес', 'sub_pro')],
          [Markup.button.callback('↩️ Назад', 'back_to_profile')]
        ]);
        await bot.editMessageText(`
<b>🔄 Управление подпиской</b>

Ваш текущий тариф: <b>${user.subscription?.type || 'Базовый'}</b>
Статус: <b>${user.subscription ? 'Активна' : 'Не активна'}</b>
${user.subscription ? `Действует до: <b>${new Date(user.subscription.endDate).toLocaleDateString()}</b>` : ''}

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
`, {
          chat_id: chatId,
          message_id: query.message.message_id,
          parse_mode: 'HTML',
          reply_markup: subKeyboard
        });
        break;

      case 'profile_payment':
        const paymentKeyboard = Markup.inlineKeyboard([
          [Markup.button.callback('💳 Оплатить 1₽', 'payment_test')],
          [Markup.button.callback('↩️ Назад', 'back_to_profile')]
        ]);
        await bot.editMessageText(`
💳 Тестовый платеж

Это демонстрация работы платежной системы.

Сумма к оплате: 1₽
Назначение: Тестовый платеж

Нажмите кнопку ниже для перехода к оплате
`, {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: paymentKeyboard
        });
        break;

      case 'profile_income':
        const income = await calculateIncome(user.id, prisma);
        await bot.editMessageText(`
💰 Ваш доход

За текущий месяц: ${income.monthly}₽
За все время: ${income.total}₽

Количество выполненных заказов: ${income.completedOrders}
Средний чек: ${income.averageOrder}₽
`, {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: Markup.inlineKeyboard([[Markup.button.callback('↩️ Назад', 'back_to_profile')]])
        });
        break;

      case 'profile_status':
        const statusKeyboard = Markup.inlineKeyboard([
          [
            Markup.button.callback('🟢 Активен', 'profile_status_active'),
            Markup.button.callback('🔴 Неактивен', 'profile_status_inactive')
          ],
          [Markup.button.callback('↩️ Назад', 'back_to_profile')]
        ]);
        await bot.editMessageText(`
🔄 Статус профиля

Текущий статус: ${user.isActive ? '🟢 Активен' : '🔴 Неактивен'}

Активный статус позволяет:
• Получать новые заказы
• Быть видимым в поиске
• Принимать заказы в работу
`, {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: statusKeyboard
        });
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
          message_id: query.message.message_id,
          reply_markup: Markup.inlineKeyboard([[Markup.button.callback('↩️ Назад', 'profile_status')]])
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
          message_id: query.message.message_id,
          reply_markup: Markup.inlineKeyboard([[Markup.button.callback('↩️ Назад', 'profile_status')]])
        });
        break;

      case 'back_to_profile':
        await showProfile(bot, chatId, user);
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

async function calculateIncome(userId, prisma) {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

  const completedOrders = await prisma.order.findMany({
    where: {
      contractorId: userId,
      status: 'COMPLETED'
    }
  });

  const monthlyOrders = completedOrders.filter(order => 
    new Date(order.completedAt) >= startOfMonth
  );

  const totalIncome = completedOrders.reduce((sum, order) => sum + (order.price || 0), 0);
  const monthlyIncome = monthlyOrders.reduce((sum, order) => sum + (order.price || 0), 0);
  const averageOrder = completedOrders.length > 0 ? totalIncome / completedOrders.length : 0;

  return {
    monthly: monthlyIncome,
    total: totalIncome,
    completedOrders: completedOrders.length,
    averageOrder: Math.round(averageOrder)
  };
}

module.exports = {
  handleProfile,
  handleProfileCallback,
  profileStates
}; 