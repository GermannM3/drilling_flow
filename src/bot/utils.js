// Форматирование профиля пользователя
async function getUserProfileText(user) {
  let text = '';
  
  switch (user.role) {
    case 'CLIENT':
      text = `🏠 <b>Профиль клиента</b>\n\n` +
             `👤 Имя: ${user.name}\n` +
             `📱 Телефон: ${user.phone || 'Не указан'}\n` +
             `📧 Email: ${user.email || 'Не указан'}\n\n` +
             `📊 Статистика:\n` +
             `- Всего заказов: ${await getOrdersCount(user.id)}\n` +
             `- Активных заказов: ${await getActiveOrdersCount(user.id)}`;
      break;
      
    case 'CONTRACTOR':
      const contractor = user.contractor;
      if (!contractor) break;
      
      text = `👷 <b>Профиль подрядчика</b>\n\n` +
             `👤 Имя: ${user.name}\n` +
             `📱 Телефон: ${user.phone || 'Не указан'}\n` +
             `📧 Email: ${user.email || 'Не указан'}\n\n` +
             `🔧 Специализация: ${contractor.specialization.join(', ')}\n` +
             `📍 Радиус работы: ${contractor.workRadius} км\n` +
             `⭐️ Рейтинг: ${contractor.rating.toFixed(1)} (${contractor.ratingCount} отзывов)\n\n` +
             `📊 Статистика:\n` +
             `- Выполнено заказов: ${await getCompletedOrdersCount(contractor.id)}\n` +
             `- Активных заказов: ${await getActiveOrdersCount(user.id)}\n` +
             `- Отменено заказов: ${await getCancelledOrdersCount(contractor.id)}`;
      break;
      
    case 'ADMIN':
      text = `👨‍💼 <b>Профиль администратора</b>\n\n` +
             `👤 Имя: ${user.name}\n` +
             `📱 Телефон: ${user.phone || 'Не указан'}\n` +
             `📧 Email: ${user.email || 'Не указан'}`;
      break;
  }
  
  return text;
}

// Получение количества заказов
async function getOrdersCount(userId) {
  try {
    const count = await prisma.order.count({
      where: { clientId: userId }
    });
    return count;
  } catch (error) {
    console.error('Ошибка при подсчете заказов:', error);
    return 0;
  }
}

// Получение количества активных заказов
async function getActiveOrdersCount(userId) {
  try {
    const count = await prisma.order.count({
      where: {
        OR: [
          { clientId: userId },
          { contractor: { userId: userId } }
        ],
        status: {
          in: ['NEW', 'PENDING', 'ACCEPTED', 'IN_PROGRESS']
        }
      }
    });
    return count;
  } catch (error) {
    console.error('Ошибка при подсчете активных заказов:', error);
    return 0;
  }
}

// Получение количества выполненных заказов
async function getCompletedOrdersCount(contractorId) {
  try {
    const count = await prisma.order.count({
      where: {
        contractorId: contractorId,
        status: 'COMPLETED'
      }
    });
    return count;
  } catch (error) {
    console.error('Ошибка при подсчете выполненных заказов:', error);
    return 0;
  }
}

// Получение количества отмененных заказов
async function getCancelledOrdersCount(contractorId) {
  try {
    const count = await prisma.order.count({
      where: {
        contractorId: contractorId,
        status: 'CANCELLED'
      }
    });
    return count;
  } catch (error) {
    console.error('Ошибка при подсчете отмененных заказов:', error);
    return 0;
  }
}

// Форматирование даты
function formatDate(date) {
  return new Date(date).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Форматирование статуса заказа
function formatOrderStatus(status) {
  const statusMap = {
    'NEW': '🆕 Новый',
    'PENDING': '⏳ Ожидает',
    'ACCEPTED': '✅ Принят',
    'IN_PROGRESS': '🔄 В работе',
    'COMPLETED': '✨ Выполнен',
    'CANCELLED': '❌ Отменен'
  };
  return statusMap[status] || status;
}

// Проверка прав администратора
async function isAdmin(userId) {
  try {
    const user = await prisma.user.findUnique({
      where: { telegramId: BigInt(userId) }
    });
    return user?.role === 'ADMIN';
  } catch (error) {
    console.error('Ошибка при проверке прав администратора:', error);
    return false;
  }
}

// Создание уведомления
async function createNotification(userId, type, message) {
  try {
    await prisma.notification.create({
      data: {
        type,
        message,
        userId
      }
    });
  } catch (error) {
    console.error('Ошибка при создании уведомления:', error);
  }
}

// Расчет расстояния между двумя точками (в километрах)
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Радиус Земли в километрах
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
           Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * 
           Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function toRad(value) {
  return value * Math.PI / 180;
}

module.exports = {
  getUserProfileText,
  getOrdersCount,
  getActiveOrdersCount,
  getCompletedOrdersCount,
  getCancelledOrdersCount,
  formatDate,
  formatOrderStatus,
  isAdmin,
  createNotification,
  calculateDistance
}; 