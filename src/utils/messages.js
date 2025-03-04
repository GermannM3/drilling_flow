/**
 * @fileoverview Утилиты для работы с сообщениями и форматированием текста
 * @module utils/messages
 */

const { formatCurrency, formatDate, getWordForm } = require('./common');

/**
 * Форматирует профиль пользователя
 * @param {Object} user - Данные пользователя
 * @returns {string} Отформатированное сообщение
 */
const formatUserProfile = (user) => {
  const stars = '⭐'.repeat(Math.round(user.rating));
  
  return `<b>📋 Профиль пользователя</b>

<b>ID:</b> ${user.id}
<b>Имя:</b> ${user.name}
<b>Статус:</b> ${user.status}
<b>Роль:</b> ${user.role}
<b>Рейтинг:</b> ${stars} (${user.rating.toFixed(1)})
<b>Выполнено заказов:</b> ${user.completedOrders}
<b>Регистрация:</b> ${user.registrationDate}

<i>Для редактирования профиля используйте меню настроек</i>`;
};

/**
 * Форматирует информацию о заказе
 * @param {Object} order - Данные заказа
 * @returns {string} Отформатированное сообщение
 */
const formatOrderInfo = (order) => {
  return `<b>Заказ #${order.id}</b> - ${order.title}, ${order.depth}м
📍 ${order.location}
💰 ${formatCurrency(order.price)}
🕒 Выполнить до: ${order.deadline}

${order.description ? `📝 ${order.description}\n` : ''}
<i>Для принятия заказа нажмите кнопку ниже</i>`;
};

/**
 * Форматирует список заказов
 * @param {Array} orders - Массив заказов
 * @returns {string} Отформатированное сообщение
 */
const formatOrdersList = (orders) => {
  if (!orders || orders.length === 0) {
    return '<b>📦 Список заказов</b>\n\nУ вас пока нет заказов. Используйте кнопку "Поиск заказов", чтобы найти подходящие предложения.';
  }
  
  const activeOrders = orders.filter(order => order.status === 'ACTIVE');
  const completedOrders = orders.filter(order => order.status === 'COMPLETED');
  
  let message = '<b>📦 Список заказов</b>\n\n';
  
  if (activeOrders.length > 0) {
    message += '<b>Активные заказы:</b>\n';
    activeOrders.forEach(order => {
      message += formatOrderInfo(order) + '\n\n';
    });
  } else {
    message += '<b>Активные заказы:</b> нет активных заказов\n\n';
  }
  
  if (completedOrders.length > 0) {
    message += '<b>Завершенные заказы:</b>\n';
    completedOrders.slice(0, 3).forEach(order => {
      message += `• Заказ #${order.id} - ${order.title}, ${order.depth}м\n`;
      message += `  ✅ Завершен ${order.completionDate}\n`;
      const stars = '⭐'.repeat(Math.round(order.rating));
      message += `  ${stars} Оценка: ${order.rating.toFixed(1)}\n\n`;
    });
  }
  
  return message;
};

/**
 * Форматирует статистику пользователя
 * @param {Object} user - Данные пользователя
 * @returns {string} Отформатированное сообщение
 */
const formatUserStats = (user) => {
  const stats = user.stats;
  const totalOrders = stats.inProgress + stats.completed + stats.cancelled;
  
  const totalReviews = stats.positiveReviews + stats.negativeReviews;
  const positivePercentage = totalReviews > 0 
    ? Math.round((stats.positiveReviews / totalReviews) * 100) 
    : 0;
  const negativePercentage = totalReviews > 0 
    ? Math.round((stats.negativeReviews / totalReviews) * 100) 
    : 0;
  
  const now = new Date();
  const updateTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  
  return `<b>📊 Статистика пользователя</b>

<b>Общая статистика:</b>
• Всего заказов: ${totalOrders}
• В работе: ${stats.inProgress}
• Завершено: ${stats.completed}
• Отменено: ${stats.cancelled}

<b>Рейтинг:</b> ${'⭐'.repeat(Math.round(user.rating))} (${user.rating.toFixed(1)})
<b>Положительных отзывов:</b> ${stats.positiveReviews} (${positivePercentage}%)
<b>Отрицательных отзывов:</b> ${stats.negativeReviews} (${negativePercentage}%)

<b>Производительность:</b>
• Среднее время выполнения: ${stats.averageCompletionTime} дня
• Соблюдение сроков: ${stats.timelyCompletionRate}%
• Качество работы: ${stats.workQuality}

<b>Финансы:</b>
• Общий доход: ${formatCurrency(user.finance.totalIncome)}
• Средний чек: ${formatCurrency(user.finance.averageCheck)}
• Бонусы: ${formatCurrency(user.finance.bonuses)}

<i>Данные обновлены: сегодня в ${updateTime}</i>`;
};

/**
 * Форматирует информацию о подписке
 * @param {Object} user - Данные пользователя
 * @returns {string} Отформатированное сообщение
 */
const formatSubscriptionInfo = (user) => {
  const subscription = user.subscription;
  const isActive = subscription.status === 'ACTIVE';
  
  let message = '<b>🔄 Подписка</b>\n\n';
  
  if (isActive) {
    const expDate = new Date(subscription.expirationDate.split('.').reverse().join('-'));
    const now = new Date();
    const diffTime = Math.abs(expDate - now);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    message += `<b>Текущий статус:</b> ${subscription.status} ✅\n`;
    message += `<b>Тариф:</b> ${subscription.plan}\n`;
    message += `<b>Дата активации:</b> ${subscription.activationDate}\n`;
    message += `<b>Действует до:</b> ${subscription.expirationDate} (осталось ${diffDays} ${getWordForm(diffDays, ['день', 'дня', 'дней'])})\n\n`;
    
    if (subscription.features?.length > 0) {
      message += '<b>Включено в тариф:</b>\n';
      subscription.features.forEach(feature => {
        message += `• ${feature}\n`;
      });
    }
  } else {
    message += '<b>Текущий статус:</b> Неактивна ❌\n\n';
    message += '<b>Доступные тарифы:</b>\n';
    message += '• Базовый - 990 ₽/месяц\n';
    message += '• Стандартный - 1,990 ₽/месяц\n';
    message += '• Премиум - 2,990 ₽/месяц\n\n';
    message += '<i>Для активации подписки выберите тариф</i>';
  }
  
  return message;
};

/**
 * Форматирует информацию о доходе
 * @param {Object} user - Данные пользователя
 * @returns {string} Отформатированное сообщение
 */
const formatIncomeInfo = (user) => {
  const finance = user.finance;
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();
  
  const months = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ];
  
  let monthlyStats = '';
  for (let i = 0; i < 4; i++) {
    let monthIndex = currentMonth - i;
    let year = currentYear;
    
    if (monthIndex < 0) {
      monthIndex += 12;
      year -= 1;
    }
    
    const monthName = months[monthIndex];
    const monthKey = `${year}-${(monthIndex + 1).toString().padStart(2, '0')}`;
    const monthIncome = finance.monthlyIncome?.[monthKey] || 0;
    const monthOrders = finance.monthlyOrders?.[monthKey] || 0;
    
    monthlyStats += `• ${monthName} ${year}: ${formatCurrency(monthIncome)} (${monthOrders} ${getWordForm(monthOrders, ['заказ', 'заказа', 'заказов'])})\n`;
  }
  
  return `<b>💰 Доход</b>

<b>Общий доход:</b> ${formatCurrency(finance.totalIncome)}

<b>Статистика по месяцам:</b>
${monthlyStats}
<b>Текущий баланс:</b> ${formatCurrency(finance.currentBalance)}
<b>Доступно к выводу:</b> ${formatCurrency(finance.currentBalance)}
<b>В обработке:</b> ${formatCurrency(finance.pendingBalance)}

<b>Способы вывода:</b>
• Банковская карта
• СБП
• Электронные кошельки

<i>Для вывода средств нажмите кнопку "Вывести"</i>`;
};

module.exports = {
  formatUserProfile,
  formatOrderInfo,
  formatOrdersList,
  formatUserStats,
  formatSubscriptionInfo,
  formatIncomeInfo
}; 