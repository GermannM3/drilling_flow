const { PrismaClient } = require('@prisma/client');
const geolib = require('geolib');

const prisma = new PrismaClient();

// Основная клавиатура
const mainKeyboard = {
  reply_markup: {
    keyboard: [
      ['📋 Профиль', '📍 Местоположение'],
      ['📦 Заказы', '⚙️ Настройки'],
      ['❓ Помощь']
    ],
    resize_keyboard: true
  }
};

// Обработчик команды /start
async function handleStart(bot, msg) {
  const chatId = msg.chat.id;
  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(msg.from.id)
      }
    });

    if (!user) {
      await prisma.user.create({
        data: {
          telegramId: BigInt(msg.from.id),
          chatId: BigInt(chatId),
          firstName: msg.from.first_name,
          lastName: msg.from.last_name,
          username: msg.from.username
        }
      });
    }

    bot.sendMessage(chatId, 'Добро пожаловать в DrillFlow! Я помогу вам найти подрядчиков для ваших работ.', mainKeyboard);
  } catch (error) {
    console.error('Ошибка при обработке команды /start:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.');
  }
}

// Обработчик команды /help
function handleHelp(bot, msg) {
  const chatId = msg.chat.id;
  const helpText = `
Доступные команды:
/start - Начать работу с ботом
/help - Показать это сообщение
/profile - Управление профилем
/settings - Настройки
/location - Обновить местоположение

Для клиентов:
- Создавайте заказы
- Находите подрядчиков поблизости
- Оставляйте отзывы

Для подрядчиков:
- Загружайте документы
- Получайте заказы
- Управляйте профилем

По всем вопросам обращайтесь в поддержку.
  `;
  bot.sendMessage(chatId, helpText, mainKeyboard);
}

// Обработчик местоположения
async function handleLocation(bot, msg) {
  const chatId = msg.chat.id;
  if (msg.location) {
    try {
      const user = await prisma.user.findFirst({
        where: {
          telegramId: BigInt(msg.from.id)
        }
      });

      if (!user) {
        bot.sendMessage(chatId, 'Пожалуйста, сначала запустите бота командой /start');
        return;
      }

      const location = await prisma.location.upsert({
        where: {
          userId: user.id
        },
        update: {
          latitude: msg.location.latitude,
          longitude: msg.location.longitude
        },
        create: {
          userId: user.id,
          latitude: msg.location.latitude,
          longitude: msg.location.longitude
        }
      });

      bot.sendMessage(chatId, 'Ваше местоположение обновлено!', mainKeyboard);

      // Если пользователь - подрядчик, ищем ближайшие заказы
      if (user.role === 'contractor') {
        const nearbyOrders = await findNearbyOrders(location);
        if (nearbyOrders.length > 0) {
          let message = 'Найдены заказы поблизости:\n\n';
          for (const order of nearbyOrders) {
            message += `📦 Заказ #${order.id}\n`;
            message += `📍 Адрес: ${order.address}\n`;
            message += `📝 Описание: ${order.description}\n`;
            message += `💰 Цена: ${order.price ? order.price + ' руб.' : 'Договорная'}\n\n`;
          }
          bot.sendMessage(chatId, message);
        }
      }
    } catch (error) {
      console.error('Ошибка при обработке местоположения:', error);
      bot.sendMessage(chatId, 'Произошла ошибка при обновлении местоположения. Пожалуйста, попробуйте позже.');
    }
  } else {
    const keyboard = {
      reply_markup: {
        keyboard: [
          [{ text: '📍 Отправить местоположение', request_location: true }],
          ['🔙 Назад']
        ],
        resize_keyboard: true
      }
    };
    bot.sendMessage(chatId, 'Пожалуйста, отправьте ваше местоположение, нажав на кнопку ниже:', keyboard);
  }
}

// Вспомогательная функция для поиска ближайших заказов
async function findNearbyOrders(location) {
  const orders = await prisma.order.findMany({
    where: {
      status: 'pending',
      latitude: { not: null },
      longitude: { not: null }
    }
  });

  const nearbyOrders = orders.filter(order => {
    const distance = geolib.getDistance(
      { latitude: location.latitude, longitude: location.longitude },
      { latitude: order.latitude, longitude: order.longitude }
    );
    // Конвертируем расстояние из метров в километры
    return distance / 1000 <= location.workRadius;
  });

  return nearbyOrders;
}

module.exports = {
  handleStart,
  handleHelp,
  handleLocation,
  mainKeyboard
}; 