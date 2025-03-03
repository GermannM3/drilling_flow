const { Markup } = require('telegraf');

async function handleSubscription(ctx) {
  try {
    const user = await ctx.prisma.user.findFirst({
      where: {
        telegramId: BigInt(ctx.from.id)
      },
      include: {
        subscription: true
      }
    });

    if (!user) {
      return ctx.reply('Пользователь не найден. Используйте /start для регистрации.');
    }

    const subscription = user.subscription;
    let message = '';
    let keyboard;

    if (subscription && new Date(subscription.endDate) > new Date()) {
      // У пользователя есть активная подписка
      message = `
📱 Ваша подписка

Тип: ${subscription.type === 'PREMIUM' ? '💎 Премиум' : '🚀 Профессионал'}
Действует до: ${new Date(subscription.endDate).toLocaleDateString()}
Автопродление: ${subscription.autoRenew ? '✅ Включено' : '❌ Выключено'}

Доступные функции:
${getSubscriptionFeatures(subscription.type)}
      `;

      keyboard = Markup.inlineKeyboard([
        [Markup.button.callback(
          subscription.autoRenew ? '❌ Отключить автопродление' : '✅ Включить автопродление',
          subscription.autoRenew ? 'sub_disable_auto' : 'sub_enable_auto'
        )],
        [Markup.button.callback('🔄 Продлить подписку', 'sub_renew')],
        [Markup.button.callback('💫 Изменить тип подписки', 'sub_change')]
      ]);
    } else {
      // У пользователя нет активной подписки
      message = `
💡 У вас нет активной подписки

Выберите тип подписки:

💎 Премиум (999₽/мес)
${getSubscriptionFeatures('PREMIUM')}

🚀 Профессионал (1999₽/мес)
${getSubscriptionFeatures('PROFESSIONAL')}
      `;

      keyboard = Markup.inlineKeyboard([
        [
          Markup.button.callback('💎 Премиум', 'payment_premium'),
          Markup.button.callback('🚀 Профессионал', 'payment_pro')
        ]
      ]);
    }

    await ctx.reply(message, keyboard);
  } catch (error) {
    console.error('Ошибка при обработке подписки:', error);
    ctx.reply('Произошла ошибка. Попробуйте позже.');
  }
}

function getSubscriptionFeatures(type) {
  const features = {
    PREMIUM: `
• Доступ к базе заказов
• Приоритетная поддержка
• Расширенная статистика
• До 50 заказов в месяц`,
    PROFESSIONAL: `
• Все функции Премиум
• Неограниченное количество заказов
• API доступ
• Персональный менеджер
• Брендированные документы`
  };

  return features[type] || '';
}

async function handleSubscriptionCallback(bot, query, prisma) {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;

  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      },
      include: {
        subscription: true
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
      case 'sub_enable_auto':
      case 'sub_disable_auto':
        if (!user.subscription) {
          await bot.answerCallbackQuery(query.id, {
            text: 'У вас нет активной подписки',
            show_alert: true
          });
          return;
        }

        await prisma.subscription.update({
          where: { id: user.subscription.id },
          data: { autoRenew: data === 'sub_enable_auto' }
        });

        await bot.answerCallbackQuery(query.id, {
          text: `Автопродление ${data === 'sub_enable_auto' ? 'включено' : 'отключено'}`,
          show_alert: true
        });

        // Обновляем сообщение с информацией о подписке
        await handleSubscription({ ...ctx, from: { id: userId } });
        break;

      case 'sub_renew':
      case 'sub_change':
        // Перенаправляем на страницу оплаты
        const keyboard = Markup.inlineKeyboard([
          [
            Markup.button.callback('💎 Премиум (999₽)', 'payment_premium'),
            Markup.button.callback('🚀 Профессионал (1999₽)', 'payment_pro')
          ]
        ]);

        await bot.editMessageText('Выберите тип подписки:', {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: keyboard
        });
        break;
    }

    await bot.answerCallbackQuery(query.id);
  } catch (error) {
    console.error('Ошибка при обработке подписки:', error);
    await bot.answerCallbackQuery(query.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Функция для проверки и обновления подписок
async function checkSubscriptions(prisma, bot) {
  try {
    const expiredSubscriptions = await prisma.subscription.findMany({
      where: {
        endDate: {
          lt: new Date()
        },
        autoRenew: true
      },
      include: {
        user: true
      }
    });

    for (const subscription of expiredSubscriptions) {
      try {
        // Создаем новый платеж для автопродления
        const payment = await prisma.payment.create({
          data: {
            userId: subscription.userId,
            amount: subscription.type === 'PREMIUM' ? 999 : 1999,
            status: 'PENDING',
            paymentMethod: 'CARD',
            description: `Автопродление подписки ${subscription.type}`
          }
        });

        // Отправляем уведомление пользователю
        await bot.telegram.sendMessage(subscription.user.telegramId, `
⚠️ Срок действия вашей подписки истек

Тип подписки: ${subscription.type === 'PREMIUM' ? '💎 Премиум' : '🚀 Профессионал'}
Сумма к оплате: ${payment.amount}₽

Для продления перейдите по ссылке:
${process.env.FRONTEND_URL}/payment/${payment.id}
        `);
      } catch (error) {
        console.error(`Ошибка при обработке подписки ${subscription.id}:`, error);
      }
    }
  } catch (error) {
    console.error('Ошибка при проверке подписок:', error);
  }
}

module.exports = {
  handleSubscription,
  handleSubscriptionCallback,
  checkSubscriptions
}; 