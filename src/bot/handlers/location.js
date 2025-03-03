const { calculateDistance } = require('../utils');

// Обработчик геолокации
async function handleLocation(bot, msg, prisma) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    const user = await prisma.user.findUnique({
      where: { telegramId: BigInt(userId) },
      include: { contractor: true }
    });

    if (!user) {
      await bot.sendMessage(chatId, 'Пользователь не найден.');
      return;
    }

    if (!msg.location) {
      await requestLocation(bot, chatId);
      return;
    }

    const { latitude, longitude } = msg.location;

    if (user.role === 'CONTRACTOR') {
      await handleContractorLocation(bot, msg, prisma, user, latitude, longitude);
    } else {
      await handleClientLocation(bot, msg, prisma, user, latitude, longitude);
    }
  } catch (error) {
    console.error('Ошибка при обработке геолокации:', error);
    await bot.sendMessage(chatId,
      'Произошла ошибка при обработке геолокации. Пожалуйста, попробуйте позже.'
    );
  }
}

// Запрос геолокации
async function requestLocation(bot, chatId) {
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

  await bot.sendMessage(chatId,
    'Для работы с геолокацией, пожалуйста, отправьте ваше местоположение:',
    { reply_markup: keyboard }
  );
}

// Обработка геолокации подрядчика
async function handleContractorLocation(bot, msg, prisma, user, latitude, longitude) {
  const chatId = msg.chat.id;

  try {
    // Обновляем или создаем запись о местоположении
    await prisma.location.upsert({
      where: {
        contractorId: user.contractor.id
      },
      update: {
        latitude,
        longitude
      },
      create: {
        latitude,
        longitude,
        contractor: {
          connect: { id: user.contractor.id }
        }
      }
    });

    // Находим ближайшие активные заказы
    const orders = await prisma.order.findMany({
      where: {
        status: 'NEW',
        location: {
          isNot: null
        }
      },
      include: {
        location: true
      }
    });

    // Фильтруем заказы по радиусу работы подрядчика
    const nearbyOrders = orders.filter(order => {
      if (!order.location) return false;
      
      const distance = calculateDistance(
        latitude,
        longitude,
        order.location.latitude,
        order.location.longitude
      );

      return distance <= user.contractor.workRadius;
    });

    // Отправляем информацию о ближайших заказах
    if (nearbyOrders.length > 0) {
      let message = '📍 Найдены заказы в вашем радиусе работы:\n\n';
      
      for (const order of nearbyOrders) {
        const distance = calculateDistance(
          latitude,
          longitude,
          order.location.latitude,
          order.location.longitude
        );

        message += `🔹 Заказ #${order.id}\n` +
                  `📍 Адрес: ${order.address}\n` +
                  `📏 Расстояние: ${distance.toFixed(1)} км\n` +
                  `🔧 Услуга: ${order.service}\n\n`;
      }

      await bot.sendMessage(chatId, message);
    } else {
      await bot.sendMessage(chatId,
        '📍 Ваша геолокация обновлена!\n' +
        'В данный момент нет заказов в вашем радиусе работы.'
      );
    }
  } catch (error) {
    console.error('Ошибка при обработке геолокации подрядчика:', error);
    await bot.sendMessage(chatId,
      'Произошла ошибка при обновлении геолокации. Пожалуйста, попробуйте позже.'
    );
  }
}

// Обработка геолокации клиента
async function handleClientLocation(bot, msg, prisma, user, latitude, longitude) {
  const chatId = msg.chat.id;

  try {
    // Находим подрядчиков поблизости
    const contractors = await prisma.contractor.findMany({
      where: {
        location: {
          isNot: null
        },
        user: {
          status: 'ACTIVE'
        }
      },
      include: {
        location: true,
        user: true
      }
    });

    // Фильтруем подрядчиков по расстоянию
    const nearbyContractors = contractors.filter(contractor => {
      if (!contractor.location) return false;

      const distance = calculateDistance(
        latitude,
        longitude,
        contractor.location.latitude,
        contractor.location.longitude
      );

      return distance <= contractor.workRadius;
    });

    if (nearbyContractors.length > 0) {
      let message = '👷 Найдены подрядчики, готовые работать в вашем районе:\n\n';

      for (const contractor of nearbyContractors) {
        const distance = calculateDistance(
          latitude,
          longitude,
          contractor.location.latitude,
          contractor.location.longitude
        );

        message += `👤 ${contractor.user.name}\n` +
                  `📏 Расстояние: ${distance.toFixed(1)} км\n` +
                  `🔧 Специализация: ${contractor.specialization.join(', ')}\n` +
                  `⭐️ Рейтинг: ${contractor.rating.toFixed(1)}\n\n`;
      }

      await bot.sendMessage(chatId, message);
    } else {
      await bot.sendMessage(chatId,
        '😔 К сожалению, в вашем районе пока нет доступных подрядчиков.\n' +
        'Попробуйте создать заказ - мы постараемся найти подрядчика!'
      );
    }
  } catch (error) {
    console.error('Ошибка при обработке геолокации клиента:', error);
    await bot.sendMessage(chatId,
      'Произошла ошибка при поиске подрядчиков. Пожалуйста, попробуйте позже.'
    );
  }
}

module.exports = {
  handleLocation
}; 