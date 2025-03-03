const { getMainMenuKeyboard } = require('../keyboards');
const { getUserProfileText } = require('../utils');

async function handleStart(bot, msg, prisma) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    // Проверяем, существует ли пользователь
    let user = await prisma.user.findUnique({
      where: { telegramId: BigInt(userId) },
      include: { contractor: true }
    });

    if (user) {
      // Если пользователь уже существует, показываем главное меню
      const welcomeBack = `С возвращением, ${user.name}! 👋\n\n${await getUserProfileText(user)}`;
      await bot.sendMessage(chatId, welcomeBack, {
        parse_mode: 'HTML',
        reply_markup: await getMainMenuKeyboard(user.role)
      });
    } else {
      // Если пользователь новый, начинаем регистрацию
      const welcome = `Добро пожаловать в DrillFlow! 🚀\n\n` +
        `Я помогу вам:\n` +
        `📝 Оформить заказ на бурение или канализацию\n` +
        `👷 Зарегистрироваться как подрядчик\n` +
        `📊 Отслеживать статус заказов\n\n` +
        `Выберите, как вы хотите использовать бота:`;

      const options = {
        reply_markup: {
          inline_keyboard: [
            [
              { text: "🏠 Я клиент", callback_data: "register_client" },
              { text: "👷 Я подрядчик", callback_data: "register_contractor" }
            ]
          ]
        }
      };

      await bot.sendMessage(chatId, welcome, options);
    }
  } catch (error) {
    console.error('Ошибка при обработке команды /start:', error);
    throw error;
  }
}

module.exports = { handleStart }; 