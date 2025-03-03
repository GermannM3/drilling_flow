const { Telegraf, Markup } = require('telegraf');
const { handleProfile } = require('./handlers/profile');
const { handleOrders } = require('./handlers/orders');
const { handlePayment, handlePaymentCallback } = require('./handlers/payments');
const { handleSubscription, handleSubscriptionCallback, checkSubscriptions } = require('./handlers/subscriptions');
const { handleSettings } = require('./handlers/settings');
const { handleDocuments } = require('./handlers/documents');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Добавляем Prisma в контекст
bot.context.prisma = prisma;

// Обработка команды /start
bot.command('start', async (ctx) => {
  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(ctx.from.id)
      }
    });

    if (!user) {
      await prisma.user.create({
        data: {
          telegramId: BigInt(ctx.from.id),
          username: ctx.from.username || '',
          firstName: ctx.from.first_name || '',
          lastName: ctx.from.last_name || '',
          role: 'USER'
        }
      });
    }

    const keyboard = Markup.keyboard([
      ['👤 Профиль', '📝 Заказы'],
      ['💳 Оплата', '📱 Подписка'],
      ['⚙️ Настройки', '📄 Документы']
    ]).resize();

    await ctx.reply(`
Добро пожаловать в Drilling Flow!

Выберите действие в меню ниже:
    `, keyboard);
  } catch (error) {
    console.error('Ошибка при обработке команды /start:', error);
    ctx.reply('Произошла ошибка. Попробуйте позже.');
  }
});

// Обработка текстовых сообщений
bot.hears('👤 Профиль', handleProfile);
bot.hears('📝 Заказы', handleOrders);
bot.hears('💳 Оплата', handlePayment);
bot.hears('📱 Подписка', handleSubscription);
bot.hears('⚙️ Настройки', handleSettings);
bot.hears('📄 Документы', handleDocuments);

// Обработка callback-запросов
bot.on('callback_query', async (ctx) => {
  const query = ctx.callbackQuery;
  const data = query.data;

  try {
    if (data.startsWith('payment_')) {
      await handlePaymentCallback(bot, query, prisma);
    } else if (data.startsWith('sub_')) {
      await handleSubscriptionCallback(bot, query, prisma);
    }
    // Другие обработчики callback-запросов...
  } catch (error) {
    console.error('Ошибка при обработке callback-запроса:', error);
    await ctx.answerCbQuery('Произошла ошибка. Попробуйте позже.');
  }
});

// Запуск проверки подписок каждый день в 00:00
const CronJob = require('cron').CronJob;
new CronJob('0 0 * * *', () => {
  checkSubscriptions(prisma, bot);
}, null, true);

// Обработка ошибок
bot.catch((err, ctx) => {
  console.error('Ошибка в боте:', err);
  ctx.reply('Произошла ошибка. Попробуйте позже.');
});

module.exports = bot; 