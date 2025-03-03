const { Markup } = require('telegraf');
const axios = require('axios');

async function handlePayment(ctx) {
  try {
    const user = await ctx.prisma.user.findFirst({
      where: {
        telegramId: BigInt(ctx.from.id)
      }
    });

    if (!user) {
      return ctx.reply('Пользователь не найден. Используйте /start для регистрации.');
    }

    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('💳 Тестовый платеж (1₽)', 'payment_test')],
      [
        Markup.button.callback('💎 Премиум (999₽)', 'payment_premium'),
        Markup.button.callback('🚀 Профессионал (1999₽)', 'payment_pro')
      ]
    ]);

    await ctx.reply('Выберите тип платежа:', keyboard);
  } catch (error) {
    console.error('Ошибка при обработке платежа:', error);
    ctx.reply('Произошла ошибка. Попробуйте позже.');
  }
}

async function handlePaymentCallback(bot, query, prisma) {
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

    let amount, description, paymentType;

    switch (data) {
      case 'payment_test':
        amount = 1;
        description = 'Тестовый платеж';
        paymentType = 'TEST';
        break;
      case 'payment_premium':
        amount = 999;
        description = 'Подписка Премиум';
        paymentType = 'PREMIUM';
        break;
      case 'payment_pro':
        amount = 1999;
        description = 'Подписка Профессионал';
        paymentType = 'PRO';
        break;
      default:
        return;
    }

    // Создаем платеж в базе данных
    const payment = await prisma.payment.create({
      data: {
        userId: user.id,
        amount,
        status: 'PENDING',
        paymentMethod: 'CARD',
        description
      }
    });

    // Создаем платеж в платежной системе
    const paymentUrl = await createPayment(payment.id, amount, description);

    const keyboard = Markup.inlineKeyboard([
      [Markup.button.url('💳 Перейти к оплате', paymentUrl)],
      [Markup.button.callback('↩️ Назад', 'back_to_payments')]
    ]);

    await bot.editMessageText(`
💳 Оплата

Сумма: ${amount}₽
Назначение: ${description}
ID платежа: ${payment.id}

Нажмите кнопку ниже для перехода к оплате
`, {
      chat_id: chatId,
      message_id: query.message.message_id,
      reply_markup: keyboard
    });

    await bot.answerCallbackQuery(query.id);
  } catch (error) {
    console.error('Ошибка при обработке платежа:', error);
    await bot.answerCallbackQuery(query.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

async function createPayment(paymentId, amount, description) {
  // В реальном проекте здесь будет интеграция с платежным шлюзом
  // Сейчас возвращаем тестовую ссылку
  return `https://drilling-flow.vercel.app/payment/${paymentId}`;
}

async function handlePaymentWebhook(req, res) {
  try {
    const { paymentId, status, signature } = req.body;

    // Проверка подписи
    if (!verifySignature(req.body, signature)) {
      return res.status(400).json({ error: 'Invalid signature' });
    }

    const payment = await prisma.payment.findUnique({
      where: { id: parseInt(paymentId) },
      include: { user: true }
    });

    if (!payment) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    // Обновляем статус платежа
    await prisma.payment.update({
      where: { id: payment.id },
      data: { status }
    });

    // Если платеж успешен и это оплата подписки
    if (status === 'COMPLETED' && (payment.description.includes('Премиум') || payment.description.includes('Профессионал'))) {
      const subType = payment.description.includes('Премиум') ? 'PREMIUM' : 'PROFESSIONAL';
      const endDate = new Date();
      endDate.setMonth(endDate.getMonth() + 1);

      // Обновляем или создаем подписку
      await prisma.subscription.upsert({
        where: { userId: payment.userId },
        update: {
          type: subType,
          endDate,
          autoRenew: true
        },
        create: {
          userId: payment.userId,
          type: subType,
          endDate,
          autoRenew: true
        }
      });

      // Отправляем уведомление пользователю
      const bot = createBot();
      await bot.telegram.sendMessage(payment.user.telegramId, `
✅ Оплата успешно проведена!

💫 Подписка ${subType} активирована
📅 Действует до: ${endDate.toLocaleDateString()}

Спасибо за использование нашего сервиса!
      `);
    }

    res.json({ success: true });
  } catch (error) {
    console.error('Ошибка при обработке вебхука:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

function verifySignature(payload, signature) {
  // В реальном проекте здесь будет проверка подписи
  return true;
}

module.exports = {
  handlePayment,
  handlePaymentCallback,
  handlePaymentWebhook
}; 