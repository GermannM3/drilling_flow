const { getOrderCreationKeyboard, getClientOrderControlKeyboard, getContractorOrderControlKeyboard } = require('../keyboards');
const { formatDate, formatOrderStatus, calculateDistance, createNotification } = require('../utils');
const { PrismaClient } = require('@prisma/client');
const { mainKeyboard } = require('./index');

const prisma = new PrismaClient();

// Состояния создания заказа
const orderStates = new Map();

// Обработчик заказов
async function handleOrders(bot, msg, prisma) {
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

    const state = orderStates.get(userId);
    if (state) {
      switch (state.step) {
        case 'AWAITING_SERVICE':
          await handleServiceInput(bot, msg, prisma, user);
          break;
        case 'AWAITING_ADDRESS':
          await handleAddressInput(bot, msg, prisma, user);
          break;
        case 'AWAITING_DESCRIPTION':
          await handleDescriptionInput(bot, msg, prisma, user);
          break;
        default:
          showOrdersMenu(bot, chatId, user);
      }
      return;
    }

    showOrdersMenu(bot, chatId, user);
  } catch (error) {
    console.error('Ошибка при обработке заказов:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при загрузке заказов. Пожалуйста, попробуйте позже.');
  }
}

function showOrdersMenu(bot, chatId, user) {
  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [{ text: '📝 Создать заказ', callback_data: 'order_create' }],
        [{ text: '📋 Мои заказы', callback_data: 'order_list' }],
        user.role === 'contractor' ? [{ text: '🔍 Поиск заказов', callback_data: 'order_search' }] : [],
        [{ text: '↩️ Назад', callback_data: 'back_to_menu' }]
      ].filter(row => row.length > 0)
    }
  };

  bot.sendMessage(chatId, 'Выберите действие:', keyboard);
}

async function handleOrderCallback(bot, query, prisma) {
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

    if (data.startsWith('order_accept_')) {
      const orderId = parseInt(data.split('_')[2]);
      const order = await prisma.order.update({
        where: { id: orderId },
        data: {
          status: 'accepted',
          contractorId: user.id
        },
        include: {
          client: true,
          contractor: true
        }
      });

      // Отправляем уведомление через WebSocket
      broadcastEvent('ORDER_UPDATED', {
        id: order.id,
        status: order.status,
        contractor: {
          id: user.id,
          firstName: user.firstName,
          lastName: user.lastName,
          phoneNumber: user.phoneNumber
        }
      });

      // Уведомляем клиента
      bot.sendMessage(order.client.chatId, `
✅ Ваш заказ #${order.id} принят!

👤 Подрядчик: ${user.firstName} ${user.lastName || ''}
📱 Телефон: ${user.phoneNumber || 'Не указан'}

Подрядчик свяжется с вами в ближайшее время.
      `);
    }

    switch (data) {
      case 'order_create':
        orderStates.set(userId, { step: 'AWAITING_SERVICE' });
        const serviceKeyboard = {
          reply_markup: {
            inline_keyboard: [
              [
                { text: '🚰 Бурение скважины', callback_data: 'service_drilling' },
                { text: '🔧 Ремонт скважины', callback_data: 'service_repair' }
              ],
              [
                { text: '🚿 Водоснабжение', callback_data: 'service_water' },
                { text: '🚽 Канализация', callback_data: 'service_sewage' }
              ],
              [{ text: '↩️ Назад', callback_data: 'back_to_orders' }]
            ]
          }
        };
        await bot.editMessageText('Выберите тип услуги:', {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: serviceKeyboard
        });
        break;

      case 'order_list':
        const orders = await prisma.order.findMany({
          where: {
            OR: [
              { clientId: user.id },
              { contractorId: user.id }
            ]
          },
          orderBy: {
            createdAt: 'desc'
          },
          take: 5
        });

        if (orders.length === 0) {
          await bot.editMessageText('У вас пока нет заказов.', {
            chat_id: chatId,
            message_id: query.message.message_id,
            reply_markup: {
              inline_keyboard: [
                [{ text: '📝 Создать заказ', callback_data: 'order_create' }],
                [{ text: '↩️ Назад', callback_data: 'back_to_orders' }]
              ]
            }
          });
        } else {
          let message = '*Ваши последние заказы:*\n\n';
          const keyboard = {
            inline_keyboard: []
          };

          for (const order of orders) {
            message += `📦 Заказ #${order.id}\n`;
            message += `🔧 Услуга: ${order.serviceType}\n`;
            message += `📍 Адрес: ${order.address || 'Не указан'}\n`;
            message += `📝 Статус: ${getOrderStatusText(order.status)}\n\n`;

            keyboard.inline_keyboard.push([
              { text: `📦 Заказ #${order.id}`, callback_data: `order_view_${order.id}` }
            ]);
          }

          keyboard.inline_keyboard.push([{ text: '↩️ Назад', callback_data: 'back_to_orders' }]);

          await bot.editMessageText(message, {
            chat_id: chatId,
            message_id: query.message.message_id,
            parse_mode: 'Markdown',
            reply_markup: keyboard
          });
        }
        break;

      case 'order_search':
        if (user.role !== 'contractor') {
          await bot.answerCallbackQuery(query.id, {
            text: 'Поиск заказов доступен только для подрядчиков',
            show_alert: true
          });
          return;
        }

        const location = await prisma.location.findUnique({
          where: { userId: user.id }
        });

        if (!location) {
          await bot.editMessageText('Для поиска заказов необходимо указать ваше местоположение.', {
            chat_id: chatId,
            message_id: query.message.message_id,
            reply_markup: {
              inline_keyboard: [
                [{ text: '📍 Указать местоположение', callback_data: 'location_set' }],
                [{ text: '↩️ Назад', callback_data: 'back_to_orders' }]
              ]
            }
          });
          break;
        }

        const nearbyOrders = await findNearbyOrders(location);
        if (nearbyOrders.length === 0) {
          await bot.editMessageText('Поблизости нет доступных заказов.', {
            chat_id: chatId,
            message_id: query.message.message_id,
            reply_markup: {
              inline_keyboard: [
                [{ text: '🔄 Обновить', callback_data: 'order_search' }],
                [{ text: '↩️ Назад', callback_data: 'back_to_orders' }]
              ]
            }
          });
        } else {
          let message = '*Доступные заказы поблизости:*\n\n';
          const keyboard = {
            inline_keyboard: []
          };

          for (const order of nearbyOrders) {
            message += `📦 Заказ #${order.id}\n`;
            message += `🔧 Услуга: ${order.serviceType}\n`;
            message += `📍 Адрес: ${order.address}\n`;
            message += `💰 Цена: ${order.price ? order.price + ' руб.' : 'Договорная'}\n\n`;

            keyboard.inline_keyboard.push([
              { text: `📦 Заказ #${order.id}`, callback_data: `order_view_${order.id}` }
            ]);
          }

          keyboard.inline_keyboard.push([
            { text: '🔄 Обновить', callback_data: 'order_search' },
            { text: '↩️ Назад', callback_data: 'back_to_orders' }
          ]);

          await bot.editMessageText(message, {
            chat_id: chatId,
            message_id: query.message.message_id,
            parse_mode: 'Markdown',
            reply_markup: keyboard
          });
        }
        break;

      case 'back_to_orders':
        showOrdersMenu(bot, chatId, user);
        break;

      default:
        if (data.startsWith('service_')) {
          const service = data.replace('service_', '');
          orderStates.set(userId, {
            step: 'AWAITING_ADDRESS',
            service: service
          });
          await bot.editMessageText('Введите адрес для выполнения работ:', {
            chat_id: chatId,
            message_id: query.message.message_id
          });
        } else if (data.startsWith('order_view_')) {
          const orderId = parseInt(data.split('_')[2]);
          const order = await prisma.order.findUnique({
            where: { id: orderId },
            include: {
              client: true,
              contractor: true
            }
          });

          if (!order) {
            await bot.answerCallbackQuery(query.id, {
              text: 'Заказ не найден',
              show_alert: true
            });
            return;
          }

          let message = `*Заказ #${order.id}*\n\n`;
          message += `🔧 Услуга: ${order.serviceType}\n`;
          message += `📍 Адрес: ${order.address}\n`;
          message += `📝 Описание: ${order.description}\n`;
          message += `💰 Цена: ${order.price ? order.price + ' руб.' : 'Договорная'}\n`;
          message += `📅 Создан: ${formatDate(order.createdAt)}\n`;
          message += `📊 Статус: ${getOrderStatusText(order.status)}\n\n`;

          if (order.contractor) {
            message += `👤 Подрядчик: ${order.contractor.firstName} ${order.contractor.lastName || ''}\n`;
            message += `📱 Телефон: ${order.contractor.phoneNumber || 'Не указан'}\n`;
          }

          const keyboard = {
            inline_keyboard: []
          };

          if (user.id === order.clientId) {
            if (order.status === 'pending') {
              keyboard.inline_keyboard.push([
                { text: '❌ Отменить заказ', callback_data: `order_cancel_${order.id}` }
              ]);
            }
          } else if (user.role === 'contractor') {
            if (order.status === 'pending') {
              keyboard.inline_keyboard.push([
                { text: '✅ Принять заказ', callback_data: `order_accept_${order.id}` }
              ]);
            } else if (order.status === 'in_progress' && order.contractorId === user.id) {
              keyboard.inline_keyboard.push([
                { text: '✨ Завершить заказ', callback_data: `order_complete_${order.id}` }
              ]);
            }
          }

          keyboard.inline_keyboard.push([{ text: '↩️ Назад', callback_data: 'back_to_orders' }]);

          await bot.editMessageText(message, {
            chat_id: chatId,
            message_id: query.message.message_id,
            parse_mode: 'Markdown',
            reply_markup: keyboard
          });
        }
    }

    await bot.answerCallbackQuery(query.id);
  } catch (error) {
    console.error('Ошибка при обработке callback заказов:', error);
    await bot.answerCallbackQuery(query.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

async function handleServiceInput(bot, msg, prisma, user) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const service = msg.text.trim();

  const validServices = ['Бурение скважины', 'Ремонт скважины', 'Водоснабжение', 'Канализация'];
  if (!validServices.includes(service)) {
    bot.sendMessage(chatId, 'Пожалуйста, выберите услугу из списка:', {
      reply_markup: {
        keyboard: validServices.map(s => [s]),
        resize_keyboard: true,
        one_time_keyboard: true
      }
    });
    return;
  }

  orderStates.set(userId, {
    step: 'AWAITING_ADDRESS',
    service: service
  });

  bot.sendMessage(chatId, 'Введите адрес для выполнения работ:');
}

async function handleAddressInput(bot, msg, prisma, user) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const address = msg.text.trim();
  const state = orderStates.get(userId);

  if (address.length < 10) {
    bot.sendMessage(chatId, 'Адрес слишком короткий. Пожалуйста, укажите полный адрес:');
    return;
  }

  orderStates.set(userId, {
    ...state,
    step: 'AWAITING_DESCRIPTION',
    address: address
  });

  bot.sendMessage(chatId, 'Опишите подробнее, что нужно сделать:');
}

async function handleDescriptionInput(bot, msg, prisma, user) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const description = msg.text.trim();
  const state = orderStates.get(userId);

  if (description.length < 10) {
    bot.sendMessage(chatId, 'Описание слишком короткое. Пожалуйста, опишите задачу подробнее:');
    return;
  }

  try {
    const order = await prisma.order.create({
      data: {
        clientId: user.id,
        serviceType: state.service,
        address: state.address,
        description: description,
        status: 'pending'
      }
    });

    orderStates.delete(userId);

    const message = `
✅ Заказ #${order.id} успешно создан!

🔧 Услуга: ${order.serviceType}
📍 Адрес: ${order.address}
📝 Описание: ${order.description}

Мы начали поиск подходящего подрядчика.`;

    bot.sendMessage(chatId, message, mainKeyboard);

    // Уведомляем подходящих подрядчиков
    notifyContractors(bot, prisma, order);
  } catch (error) {
    console.error('Ошибка при создании заказа:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.', mainKeyboard);
  }
}

async function notifyContractors(bot, prisma, order) {
  try {
    const contractors = await prisma.user.findMany({
      where: {
        role: 'contractor',
        isActive: true
      },
      include: {
        location: true
      }
    });

    for (const contractor of contractors) {
      if (contractor.location) {
        const distance = calculateDistance(
          order.latitude,
          order.longitude,
          contractor.location.latitude,
          contractor.location.longitude
        );

        if (distance <= contractor.location.workRadius) {
          const message = `
🆕 Новый заказ #${order.id}!

🔧 Услуга: ${order.serviceType}
📍 Адрес: ${order.address}
📝 Описание: ${order.description}

Нажмите кнопку ниже, чтобы принять заказ:`;

          bot.sendMessage(contractor.chatId, message, {
            reply_markup: {
              inline_keyboard: [
                [{ text: '✅ Принять заказ', callback_data: `order_accept_${order.id}` }]
              ]
            }
          });
        }
      }
    }
  } catch (error) {
    console.error('Ошибка при уведомлении подрядчиков:', error);
  }
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Радиус Земли в километрах
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRad(value) {
  return (value * Math.PI) / 180;
}

function getOrderStatusText(status) {
  const statuses = {
    pending: '⏳ Ожидает подрядчика',
    accepted: '✅ Принят',
    in_progress: '🔧 В работе',
    completed: '✨ Завершен',
    cancelled: '❌ Отменен'
  };
  return statuses[status] || status;
}

function formatDate(date) {
  return new Date(date).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

module.exports = {
  handleOrders,
  handleOrderCallback,
  orderStates
}; 