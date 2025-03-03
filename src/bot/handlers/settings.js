const { Markup } = require('telegraf');

// Состояния настроек
const settingsStates = new Map();

// Обработчик настроек
async function handleSettings(ctx) {
  try {
    const user = await ctx.prisma.user.findFirst({
      where: {
        telegramId: BigInt(ctx.from.id)
      },
      include: {
        settings: true
      }
    });

    if (!user) {
      return ctx.reply('Пользователь не найден. Используйте /start для регистрации.');
    }

    // Создаем настройки по умолчанию, если их нет
    if (!user.settings) {
      await ctx.prisma.settings.create({
        data: {
          userId: user.id,
          notificationsEnabled: true,
          soundEnabled: true,
          language: 'ru',
          orderRadius: 10,
          theme: 'LIGHT'
        }
      });
    }

    const settings = user.settings || {};
    const message = `
⚙️ Настройки

🔔 Уведомления: ${settings.notificationsEnabled ? '✅' : '❌'}
🔊 Звук: ${settings.soundEnabled ? '✅' : '❌'}
🌍 Язык: ${getLanguageName(settings.language)}
📍 Радиус поиска: ${settings.orderRadius} км
🎨 Тема: ${settings.theme === 'LIGHT' ? '☀️ Светлая' : '🌙 Темная'}
    `;

    const keyboard = Markup.inlineKeyboard([
      [
        Markup.button.callback(
          settings.notificationsEnabled ? '🔕 Отключить уведомления' : '🔔 Включить уведомления',
          'settings_notifications'
        )
      ],
      [
        Markup.button.callback(
          settings.soundEnabled ? '🔇 Отключить звук' : '🔊 Включить звук',
          'settings_sound'
        )
      ],
      [
        Markup.button.callback('🌍 Изменить язык', 'settings_language'),
        Markup.button.callback('📍 Изменить радиус', 'settings_radius')
      ],
      [
        Markup.button.callback(
          settings.theme === 'LIGHT' ? '🌙 Темная тема' : '☀️ Светлая тема',
          'settings_theme'
        )
      ]
    ]);

    await ctx.reply(message, keyboard);
  } catch (error) {
    console.error('Ошибка при обработке настроек:', error);
    ctx.reply('Произошла ошибка. Попробуйте позже.');
  }
}

function getLanguageName(code) {
  const languages = {
    ru: '🇷🇺 Русский',
    en: '🇬🇧 English',
    kz: '🇰🇿 Қазақша'
  };
  return languages[code] || code;
}

// Обработка callback-запросов настроек
async function handleSettingsCallback(bot, query, prisma) {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;

  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      },
      include: {
        settings: true
      }
    });

    if (!user || !user.settings) {
      await bot.answerCallbackQuery(query.id, {
        text: 'Настройки не найдены',
        show_alert: true
      });
      return;
    }

    switch (data) {
      case 'settings_notifications':
        await prisma.settings.update({
          where: { id: user.settings.id },
          data: { notificationsEnabled: !user.settings.notificationsEnabled }
        });
        break;

      case 'settings_sound':
        await prisma.settings.update({
          where: { id: user.settings.id },
          data: { soundEnabled: !user.settings.soundEnabled }
        });
        break;

      case 'settings_theme':
        await prisma.settings.update({
          where: { id: user.settings.id },
          data: { theme: user.settings.theme === 'LIGHT' ? 'DARK' : 'LIGHT' }
        });
        break;

      case 'settings_language':
        const languageKeyboard = Markup.inlineKeyboard([
          [
            Markup.button.callback('🇷🇺 Русский', 'lang_ru'),
            Markup.button.callback('🇬🇧 English', 'lang_en')
          ],
          [Markup.button.callback('🇰🇿 Қазақша', 'lang_kz')],
          [Markup.button.callback('↩️ Назад', 'settings_back')]
        ]);

        await bot.editMessageText('Выберите язык:', {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: languageKeyboard
        });
        return;

      case 'settings_radius':
        const radiusKeyboard = Markup.inlineKeyboard([
          [
            Markup.button.callback('5 км', 'radius_5'),
            Markup.button.callback('10 км', 'radius_10'),
            Markup.button.callback('20 км', 'radius_20')
          ],
          [
            Markup.button.callback('50 км', 'radius_50'),
            Markup.button.callback('100 км', 'radius_100')
          ],
          [Markup.button.callback('↩️ Назад', 'settings_back')]
        ]);

        await bot.editMessageText('Выберите радиус поиска заказов:', {
          chat_id: chatId,
          message_id: query.message.message_id,
          reply_markup: radiusKeyboard
        });
        return;
    }

    // Обработка выбора языка
    if (data.startsWith('lang_')) {
      const language = data.split('_')[1];
      await prisma.settings.update({
        where: { id: user.settings.id },
        data: { language }
      });
    }

    // Обработка выбора радиуса
    if (data.startsWith('radius_')) {
      const radius = parseInt(data.split('_')[1]);
      await prisma.settings.update({
        where: { id: user.settings.id },
        data: { orderRadius: radius }
      });
    }

    // Обновляем сообщение с настройками
    if (data === 'settings_back' || data.startsWith('lang_') || data.startsWith('radius_')) {
      const updatedUser = await prisma.user.findFirst({
        where: { telegramId: BigInt(userId) },
        include: { settings: true }
      });

      const settings = updatedUser.settings;
      const message = `
⚙️ Настройки

🔔 Уведомления: ${settings.notificationsEnabled ? '✅' : '❌'}
🔊 Звук: ${settings.soundEnabled ? '✅' : '❌'}
🌍 Язык: ${getLanguageName(settings.language)}
📍 Радиус поиска: ${settings.orderRadius} км
🎨 Тема: ${settings.theme === 'LIGHT' ? '☀️ Светлая' : '🌙 Темная'}
      `;

      const keyboard = Markup.inlineKeyboard([
        [
          Markup.button.callback(
            settings.notificationsEnabled ? '🔕 Отключить уведомления' : '🔔 Включить уведомления',
            'settings_notifications'
          )
        ],
        [
          Markup.button.callback(
            settings.soundEnabled ? '🔇 Отключить звук' : '🔊 Включить звук',
            'settings_sound'
          )
        ],
        [
          Markup.button.callback('🌍 Изменить язык', 'settings_language'),
          Markup.button.callback('📍 Изменить радиус', 'settings_radius')
        ],
        [
          Markup.button.callback(
            settings.theme === 'LIGHT' ? '🌙 Темная тема' : '☀️ Светлая тема',
            'settings_theme'
          )
        ]
      ]);

      await bot.editMessageText(message, {
        chat_id: chatId,
        message_id: query.message.message_id,
        reply_markup: keyboard
      });
    }

    await bot.answerCallbackQuery(query.id);
  } catch (error) {
    console.error('Ошибка при обработке настроек:', error);
    await bot.answerCallbackQuery(query.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

module.exports = {
  handleSettings,
  handleSettingsCallback,
  settingsStates
}; 