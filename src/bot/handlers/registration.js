const { getContractorRegistrationKeyboard } = require('../keyboards');

// Состояния регистрации
const registrationStates = new Map();

// Обработчик регистрации
async function handleRegistration(bot, msg, prisma) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const state = registrationStates.get(userId) || { step: 'NONE' };

  try {
    switch (state.step) {
      case 'NONE':
        // Начало регистрации
        await startRegistration(bot, msg);
        break;

      case 'AWAITING_NAME':
        // Получение имени
        await handleNameInput(bot, msg, prisma, state);
        break;

      case 'AWAITING_PHONE':
        // Получение телефона
        await handlePhoneInput(bot, msg, prisma, state);
        break;

      case 'AWAITING_SPECIALIZATION':
        // Получение специализации (только для подрядчиков)
        await handleSpecializationInput(bot, msg, prisma, state);
        break;

      case 'AWAITING_WORK_RADIUS':
        // Получение радиуса работы (только для подрядчиков)
        await handleWorkRadiusInput(bot, msg, prisma, state);
        break;

      default:
        // Если состояние неизвестно, начинаем регистрацию заново
        await startRegistration(bot, msg);
    }
  } catch (error) {
    console.error('Ошибка при регистрации:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.');
    registrationStates.delete(userId);
  }
}

// Начало регистрации
async function startRegistration(bot, msg) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  registrationStates.set(userId, {
    step: 'AWAITING_NAME',
    role: 'CLIENT' // По умолчанию регистрируем как клиента
  });

  await bot.sendMessage(chatId, 
    'Добро пожаловать! Давайте начнем регистрацию.\n\n' +
    'Пожалуйста, введите ваше имя:'
  );
}

// Обработка ввода имени
async function handleNameInput(bot, msg, prisma, state) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const name = msg.text.trim();

  if (name.length < 2) {
    await bot.sendMessage(chatId, 'Имя должно содержать минимум 2 символа. Попробуйте еще раз:');
    return;
  }

  state.name = name;
  state.step = 'AWAITING_PHONE';
  registrationStates.set(userId, state);

  await bot.sendMessage(chatId,
    'Отлично! Теперь введите ваш номер телефона в формате +7XXXXXXXXXX:'
  );
}

// Обработка ввода телефона
async function handlePhoneInput(bot, msg, prisma, state) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const phone = msg.text.trim();

  // Проверка формата телефона
  const phoneRegex = /^\+7\d{10}$/;
  if (!phoneRegex.test(phone)) {
    await bot.sendMessage(chatId,
      'Неверный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX:'
    );
    return;
  }

  state.phone = phone;

  if (state.role === 'CONTRACTOR') {
    state.step = 'AWAITING_SPECIALIZATION';
    registrationStates.set(userId, state);

    await bot.sendMessage(chatId,
      'Выберите вашу специализацию:',
      { reply_markup: getContractorRegistrationKeyboard() }
    );
  } else {
    // Для клиента завершаем регистрацию
    await finishRegistration(bot, msg, prisma, state);
  }
}

// Обработка выбора специализации
async function handleSpecializationInput(bot, msg, prisma, state) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const specialization = msg.text.trim();

  state.specialization = specialization;
  state.step = 'AWAITING_WORK_RADIUS';
  registrationStates.set(userId, state);

  await bot.sendMessage(chatId,
    'Укажите максимальный радиус работы в километрах (от 1 до 100):'
  );
}

// Обработка ввода радиуса работы
async function handleWorkRadiusInput(bot, msg, prisma, state) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  const radius = parseInt(msg.text.trim());

  if (isNaN(radius) || radius < 1 || radius > 100) {
    await bot.sendMessage(chatId,
      'Пожалуйста, введите число от 1 до 100:'
    );
    return;
  }

  state.workRadius = radius;
  await finishRegistration(bot, msg, prisma, state);
}

// Завершение регистрации
async function finishRegistration(bot, msg, prisma, state) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    // Создаем пользователя
    const user = await prisma.user.create({
      data: {
        telegramId: BigInt(userId),
        name: state.name,
        phone: state.phone,
        role: state.role,
        contractor: state.role === 'CONTRACTOR' ? {
          create: {
            specialization: [state.specialization],
            workRadius: state.workRadius
          }
        } : undefined
      }
    });

    // Очищаем состояние регистрации
    registrationStates.delete(userId);

    // Отправляем приветственное сообщение
    const welcomeMessage = state.role === 'CONTRACTOR'
      ? 'Регистрация завершена! Ваша заявка отправлена на модерацию. Мы уведомим вас о результатах проверки.'
      : 'Регистрация успешно завершена! Теперь вы можете создавать заказы и пользоваться всеми функциями бота.';

    await bot.sendMessage(chatId, welcomeMessage);

    // Если это подрядчик, создаем уведомление для администраторов
    if (state.role === 'CONTRACTOR') {
      // Находим всех администраторов
      const admins = await prisma.user.findMany({
        where: { role: 'ADMIN' }
      });

      // Отправляем уведомления администраторам
      for (const admin of admins) {
        if (admin.telegramId) {
          await bot.sendMessage(admin.telegramId,
            `🆕 Новая заявка на регистрацию подрядчика!\n\n` +
            `👤 Имя: ${user.name}\n` +
            `📱 Телефон: ${user.phone}\n` +
            `🔧 Специализация: ${state.specialization}\n` +
            `📍 Радиус работы: ${state.workRadius} км`
          );
        }
      }
    }
  } catch (error) {
    console.error('Ошибка при завершении регистрации:', error);
    await bot.sendMessage(chatId,
      'Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.'
    );
  }
}

module.exports = {
  handleRegistration,
  registrationStates
}; 