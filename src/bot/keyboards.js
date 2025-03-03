// Главное меню для разных ролей
async function getMainMenuKeyboard(role) {
  switch (role) {
    case 'CLIENT':
      return {
        inline_keyboard: [
          [
            { text: "📝 Новый заказ", callback_data: "new_order" },
            { text: "📊 Мои заказы", callback_data: "my_orders" }
          ],
          [
            { text: "👤 Профиль", callback_data: "profile" },
            { text: "⭐️ Отзывы", callback_data: "reviews" }
          ],
          [
            { text: "❓ Помощь", callback_data: "help" },
            { text: "⚙️ Настройки", callback_data: "settings" }
          ]
        ]
      };

    case 'CONTRACTOR':
      return {
        inline_keyboard: [
          [
            { text: "📋 Активные заказы", callback_data: "active_orders" },
            { text: "📊 История заказов", callback_data: "order_history" }
          ],
          [
            { text: "👤 Профиль", callback_data: "profile" },
            { text: "📍 Геолокация", callback_data: "location" }
          ],
          [
            { text: "📄 Документы", callback_data: "documents" },
            { text: "⭐️ Рейтинг", callback_data: "rating" }
          ],
          [
            { text: "⚙️ Настройки", callback_data: "settings" },
            { text: "❓ Помощь", callback_data: "help" }
          ]
        ]
      };

    case 'ADMIN':
      return {
        inline_keyboard: [
          [
            { text: "👥 Пользователи", callback_data: "admin_users" },
            { text: "📊 Статистика", callback_data: "admin_stats" }
          ],
          [
            { text: "✅ Модерация", callback_data: "admin_moderation" },
            { text: "📢 Рассылка", callback_data: "admin_broadcast" }
          ],
          [
            { text: "⚙️ Настройки", callback_data: "admin_settings" },
            { text: "❓ Помощь", callback_data: "help" }
          ]
        ]
      };

    default:
      return {
        inline_keyboard: [
          [
            { text: "❓ Помощь", callback_data: "help" }
          ]
        ]
      };
  }
}

// Клавиатура для регистрации подрядчика
function getContractorRegistrationKeyboard() {
  return {
    inline_keyboard: [
      [
        { text: "🚰 Бурение", callback_data: "spec_drilling" },
        { text: "🚽 Канализация", callback_data: "spec_sewage" }
      ],
      [
        { text: "🔧 Ремонт скважин", callback_data: "spec_repair" }
      ],
      [
        { text: "✅ Подтвердить выбор", callback_data: "spec_confirm" }
      ]
    ]
  };
}

// Клавиатура для создания заказа
function getOrderCreationKeyboard() {
  return {
    inline_keyboard: [
      [
        { text: "🚰 Бурение скважины", callback_data: "order_drilling" },
        { text: "🚽 Канализация", callback_data: "order_sewage" }
      ],
      [
        { text: "🔧 Ремонт скважины", callback_data: "order_repair" }
      ],
      [
        { text: "❌ Отмена", callback_data: "order_cancel" }
      ]
    ]
  };
}

// Клавиатура для управления заказом (для клиента)
function getClientOrderControlKeyboard(orderId, status) {
  const keyboard = [
    [
      { text: "📝 Детали заказа", callback_data: `order_details_${orderId}` },
      { text: "💬 Чат", callback_data: `order_chat_${orderId}` }
    ]
  ];

  if (status === 'NEW' || status === 'PENDING') {
    keyboard.push([
      { text: "❌ Отменить заказ", callback_data: `order_cancel_${orderId}` }
    ]);
  }

  if (status === 'COMPLETED') {
    keyboard.push([
      { text: "⭐️ Оставить отзыв", callback_data: `order_review_${orderId}` }
    ]);
  }

  return { inline_keyboard: keyboard };
}

// Клавиатура для управления заказом (для подрядчика)
function getContractorOrderControlKeyboard(orderId, status) {
  const keyboard = [
    [
      { text: "📝 Детали заказа", callback_data: `order_details_${orderId}` },
      { text: "💬 Чат", callback_data: `order_chat_${orderId}` }
    ]
  ];

  switch (status) {
    case 'NEW':
      keyboard.push([
        { text: "✅ Принять заказ", callback_data: `order_accept_${orderId}` },
        { text: "❌ Отклонить", callback_data: `order_reject_${orderId}` }
      ]);
      break;
    case 'ACCEPTED':
      keyboard.push([
        { text: "▶️ Начать работу", callback_data: `order_start_${orderId}` }
      ]);
      break;
    case 'IN_PROGRESS':
      keyboard.push([
        { text: "✅ Завершить заказ", callback_data: `order_complete_${orderId}` }
      ]);
      break;
  }

  return { inline_keyboard: keyboard };
}

// Клавиатура настроек
function getSettingsKeyboard() {
  return {
    inline_keyboard: [
      [
        { text: "📱 Уведомления", callback_data: "settings_notifications" },
        { text: "👤 Профиль", callback_data: "settings_profile" }
      ],
      [
        { text: "📍 Геолокация", callback_data: "settings_location" },
        { text: "🔔 Звук", callback_data: "settings_sound" }
      ],
      [
        { text: "↩️ Назад", callback_data: "back_to_menu" }
      ]
    ]
  };
}

// Клавиатура для модерации (админ)
function getModerationKeyboard(userId) {
  return {
    inline_keyboard: [
      [
        { text: "✅ Одобрить", callback_data: `moderate_approve_${userId}` },
        { text: "❌ Отклонить", callback_data: `moderate_reject_${userId}` }
      ],
      [
        { text: "👤 Профиль", callback_data: `moderate_profile_${userId}` },
        { text: "📄 Документы", callback_data: `moderate_docs_${userId}` }
      ],
      [
        { text: "⛔️ Заблокировать", callback_data: `moderate_block_${userId}` }
      ]
    ]
  };
}

module.exports = {
  getMainMenuKeyboard,
  getContractorRegistrationKeyboard,
  getOrderCreationKeyboard,
  getClientOrderControlKeyboard,
  getContractorOrderControlKeyboard,
  getSettingsKeyboard,
  getModerationKeyboard
}; 