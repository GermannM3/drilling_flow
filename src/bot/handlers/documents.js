// Состояния загрузки документов
const documentUploadStates = new Map();

// Обработчик документов
async function handleDocuments(bot, msg, prisma, type = 'document') {
  const chatId = msg.chat.id;
  const userId = msg.from.id;

  try {
    const user = await prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      },
      include: {
        documents: true
      }
    });

    if (!user) {
      bot.sendMessage(chatId, 'Пожалуйста, сначала запустите бота командой /start');
      return;
    }

    if (msg.document || msg.photo) {
      // Получаем file_id
      const fileId = msg.document ? msg.document.file_id : msg.photo[msg.photo.length - 1].file_id;
      const fileName = msg.document ? msg.document.file_name : 'photo.jpg';

      // Создаем новый документ
      await prisma.document.create({
        data: {
          userId: user.id,
          type: type,
          fileId: fileId,
          status: 'pending'
        }
      });

      bot.sendMessage(chatId, `✅ Документ "${fileName}" успешно загружен и отправлен на проверку.`);

      // Отправляем уведомление администраторам
      const admins = await prisma.user.findMany({
        where: {
          role: 'admin'
        }
      });

      for (const admin of admins) {
        const adminMessage = `
📄 *Новый документ на проверку*

*От*: ${user.firstName} ${user.lastName} (${user.username || 'нет username'})
*Тип*: ${type}
*Статус*: На проверке`;

        bot.sendMessage(admin.chatId, adminMessage, { parse_mode: 'Markdown' });
        if (type === 'photo') {
          bot.sendPhoto(admin.chatId, fileId);
        } else {
          bot.sendDocument(admin.chatId, fileId);
        }
      }
    } else {
      const keyboard = {
        reply_markup: {
          inline_keyboard: [
            [{ text: '📷 Загрузить фото', callback_data: 'document_photo' }],
            [{ text: '📄 Загрузить документ', callback_data: 'document_file' }],
            [{ text: '📋 Мои документы', callback_data: 'document_list' }],
            [{ text: '↩️ Назад', callback_data: 'back_to_menu' }]
          ]
        }
      };

      const documentsText = `
📄 *Документы*

*Загружено документов*: ${user.documents.length}
*На проверке*: ${user.documents.filter(doc => doc.status === 'pending').length}
*Проверено*: ${user.documents.filter(doc => doc.status === 'verified').length}
*Отклонено*: ${user.documents.filter(doc => doc.status === 'rejected').length}

_Выберите действие:_`;

      bot.sendMessage(chatId, documentsText, {
        parse_mode: 'Markdown',
        ...keyboard
      });
    }
  } catch (error) {
    console.error('Ошибка при обработке документов:', error);
    bot.sendMessage(chatId, 'Произошла ошибка при обработке документов. Пожалуйста, попробуйте позже.');
  }
}

// Показать меню документов
async function showDocumentsMenu(bot, chatId, user) {
  const documents = await prisma.document.findMany({
    where: { contractorId: user.contractor.id }
  });

  let message = '📄 Ваши документы:\n\n';
  
  if (documents.length > 0) {
    documents.forEach((doc, index) => {
      message += `${index + 1}. ${doc.type} - ` +
                `${doc.verified ? '✅ Проверен' : '⏳ На проверке'}\n`;
    });
  } else {
    message += 'У вас пока нет загруженных документов.\n';
  }

  message += '\nВыберите тип документа для загрузки:';

  const keyboard = {
    inline_keyboard: [
      [
        { text: "📷 Фото техники", callback_data: "doc_equipment" },
        { text: "📜 Лицензия", callback_data: "doc_license" }
      ],
      [
        { text: "🏢 Документы организации", callback_data: "doc_company" },
        { text: "📋 Сертификаты", callback_data: "doc_certificates" }
      ],
      [
        { text: "↩️ Назад", callback_data: "back_to_menu" }
      ]
    ]
  };

  await bot.sendMessage(chatId, message, { reply_markup: keyboard });
}

// Обработка фото как документа
async function handlePhotoDocument(bot, msg, prisma, user, state) {
  const chatId = msg.chat.id;
  const photoId = msg.photo[msg.photo.length - 1].file_id;

  try {
    // Создаем документ
    await prisma.document.create({
      data: {
        type: state.documentType,
        url: photoId,
        contractor: {
          connect: { id: user.contractor.id }
        }
      }
    });

    // Очищаем состояние
    documentUploadStates.delete(msg.from.id);

    // Отправляем подтверждение
    await bot.sendMessage(chatId,
      '✅ Документ успешно загружен и отправлен на проверку!'
    );

    // Уведомляем администраторов
    await notifyAdminsAboutNewDocument(bot, prisma, user, state.documentType);
  } catch (error) {
    console.error('Ошибка при сохранении фото-документа:', error);
    await bot.sendMessage(chatId,
      'Произошла ошибка при сохранении документа. Пожалуйста, попробуйте позже.'
    );
  }
}

// Обработка файла как документа
async function handleFileDocument(bot, msg, prisma, user, state) {
  const chatId = msg.chat.id;
  const fileId = msg.document.file_id;

  try {
    // Проверяем тип файла
    const allowedMimeTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!allowedMimeTypes.includes(msg.document.mime_type)) {
      await bot.sendMessage(chatId,
        'Неподдерживаемый тип файла. Пожалуйста, отправьте PDF или изображение.'
      );
      return;
    }

    // Создаем документ
    await prisma.document.create({
      data: {
        type: state.documentType,
        url: fileId,
        contractor: {
          connect: { id: user.contractor.id }
        }
      }
    });

    // Очищаем состояние
    documentUploadStates.delete(msg.from.id);

    // Отправляем подтверждение
    await bot.sendMessage(chatId,
      '✅ Документ успешно загружен и отправлен на проверку!'
    );

    // Уведомляем администраторов
    await notifyAdminsAboutNewDocument(bot, prisma, user, state.documentType);
  } catch (error) {
    console.error('Ошибка при сохранении файла-документа:', error);
    await bot.sendMessage(chatId,
      'Произошла ошибка при сохранении документа. Пожалуйста, попробуйте позже.'
    );
  }
}

// Уведомление администраторов о новом документе
async function notifyAdminsAboutNewDocument(bot, prisma, user, documentType) {
  try {
    const admins = await prisma.user.findMany({
      where: { role: 'ADMIN' }
    });

    const message = 
      `📄 Новый документ на проверку!\n\n` +
      `👤 Подрядчик: ${user.name}\n` +
      `📱 Телефон: ${user.phone}\n` +
      `📋 Тип документа: ${documentType}`;

    for (const admin of admins) {
      if (admin.telegramId) {
        await bot.sendMessage(admin.telegramId, message);
      }
    }
  } catch (error) {
    console.error('Ошибка при уведомлении администраторов:', error);
  }
}

// Обработка callback-запросов документов
async function handleDocumentCallback(bot, callbackQuery, prisma) {
  const chatId = callbackQuery.message.chat.id;
  const userId = callbackQuery.from.id;
  const data = callbackQuery.data;

  try {
    const user = await prisma.user.findUnique({
      where: { telegramId: BigInt(userId) },
      include: { contractor: true }
    });

    if (!user || user.role !== 'CONTRACTOR') {
      await bot.answerCallbackQuery(callbackQuery.id, {
        text: 'Доступ запрещен',
        show_alert: true
      });
      return;
    }

    if (data.startsWith('doc_')) {
      const documentType = data.replace('doc_', '');
      documentUploadStates.set(userId, { documentType });

      await bot.editMessageText(
        `Пожалуйста, отправьте ${getDocumentTypeDescription(documentType)}:`,
        {
          chat_id: chatId,
          message_id: callbackQuery.message.message_id
        }
      );
    }

    await bot.answerCallbackQuery(callbackQuery.id);
  } catch (error) {
    console.error('Ошибка при обработке callback документов:', error);
    await bot.answerCallbackQuery(callbackQuery.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

// Получить описание типа документа
function getDocumentTypeDescription(type) {
  const descriptions = {
    'equipment': 'фотографии вашей техники',
    'license': 'фото или скан лицензии',
    'company': 'документы организации (PDF или фото)',
    'certificates': 'сертификаты или дипломы'
  };
  return descriptions[type] || 'документ';
}

module.exports = {
  handleDocuments,
  handleDocumentCallback,
  documentUploadStates
}; 