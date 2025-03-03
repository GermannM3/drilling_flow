const { Markup } = require('telegraf');
const axios = require('axios');
const FormData = require('form-data');

// Состояния загрузки документов
const documentStates = new Map();

async function handleDocuments(ctx) {
  try {
    const user = await ctx.prisma.user.findFirst({
      where: {
        telegramId: BigInt(ctx.from.id)
      },
      include: {
        documents: true
      }
    });

    if (!user) {
      return ctx.reply('Пользователь не найден. Используйте /start для регистрации.');
    }

    const documents = user.documents || [];
    let message = '📄 Ваши документы:\n\n';

    if (documents.length === 0) {
      message += 'У вас пока нет загруженных документов.';
    } else {
      documents.forEach((doc, index) => {
        message += `${index + 1}. ${getDocumentTypeName(doc.type)} - ${doc.verified ? '✅ Проверен' : '⏳ На проверке'}\n`;
      });
    }

    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('📎 Загрузить паспорт', 'doc_upload_passport')],
      [Markup.button.callback('📎 Загрузить ИНН', 'doc_upload_inn')],
      [Markup.button.callback('📎 Загрузить СНИЛС', 'doc_upload_snils')],
      user.role === 'CONTRACTOR' ? [Markup.button.callback('📎 Загрузить документы ИП/ООО', 'doc_upload_business')] : [],
      [Markup.button.callback('🗑 Удалить документ', 'doc_delete')]
    ].filter(row => row.length > 0));

    await ctx.reply(message, keyboard);
  } catch (error) {
    console.error('Ошибка при обработке документов:', error);
    ctx.reply('Произошла ошибка. Попробуйте позже.');
  }
}

function getDocumentTypeName(type) {
  const types = {
    PASSPORT: '📕 Паспорт',
    INN: '📗 ИНН',
    SNILS: '📘 СНИЛС',
    BUSINESS: '📙 Документы ИП/ООО'
  };
  return types[type] || type;
}

async function handleDocumentCallback(bot, query, prisma) {
  const chatId = query.message.chat.id;
  const userId = query.from.id;
  const data = query.data;

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
      await bot.answerCallbackQuery(query.id, {
        text: 'Пользователь не найден',
        show_alert: true
      });
      return;
    }

    if (data.startsWith('doc_upload_')) {
      const docType = data.replace('doc_upload_', '').toUpperCase();
      
      // Проверяем, не загружен ли уже такой документ
      const existingDoc = user.documents.find(doc => doc.type === docType);
      if (existingDoc) {
        await bot.answerCallbackQuery(query.id, {
          text: 'Этот тип документа уже загружен. Удалите старый документ для загрузки нового.',
          show_alert: true
        });
        return;
      }

      // Сохраняем состояние загрузки
      documentStates.set(userId, { type: docType });

      await bot.editMessageText(`
📤 Загрузка документа: ${getDocumentTypeName(docType)}

Пожалуйста, отправьте фото или скан документа.
Поддерживаемые форматы: JPG, PNG, PDF

⚠️ Требования к документам:
- Хорошее качество изображения
- Все данные должны быть четко видны
- Размер файла не более 10 МБ
      `, {
        chat_id: chatId,
        message_id: query.message.message_id,
        reply_markup: Markup.inlineKeyboard([
          [Markup.button.callback('↩️ Отмена', 'doc_cancel')]
        ])
      });
    } else if (data === 'doc_delete') {
      if (user.documents.length === 0) {
        await bot.answerCallbackQuery(query.id, {
          text: 'У вас нет загруженных документов',
          show_alert: true
        });
        return;
      }

      const keyboard = Markup.inlineKeyboard(
        user.documents.map(doc => [
          Markup.button.callback(
            `🗑 ${getDocumentTypeName(doc.type)}`,
            `doc_delete_${doc.id}`
          )
        ]).concat([[Markup.button.callback('↩️ Назад', 'doc_back')]])
      );

      await bot.editMessageText('Выберите документ для удаления:', {
        chat_id: chatId,
        message_id: query.message.message_id,
        reply_markup: keyboard
      });
    } else if (data.startsWith('doc_delete_')) {
      const docId = parseInt(data.replace('doc_delete_', ''));
      await prisma.document.delete({
        where: { id: docId }
      });

      await bot.answerCallbackQuery(query.id, {
        text: 'Документ успешно удален',
        show_alert: true
      });

      // Обновляем список документов
      await handleDocuments({ ...ctx, from: { id: userId } });
    } else if (data === 'doc_cancel') {
      documentStates.delete(userId);
      await handleDocuments({ ...ctx, from: { id: userId } });
    } else if (data === 'doc_back') {
      await handleDocuments({ ...ctx, from: { id: userId } });
    }

    await bot.answerCallbackQuery(query.id);
  } catch (error) {
    console.error('Ошибка при обработке документов:', error);
    await bot.answerCallbackQuery(query.id, {
      text: 'Произошла ошибка. Пожалуйста, попробуйте позже.',
      show_alert: true
    });
  }
}

async function handleDocumentUpload(ctx) {
  try {
    const userId = ctx.from.id;
    const state = documentStates.get(userId);

    if (!state) {
      return ctx.reply('Сначала выберите тип документа для загрузки.');
    }

    const user = await ctx.prisma.user.findFirst({
      where: {
        telegramId: BigInt(userId)
      }
    });

    if (!user) {
      return ctx.reply('Пользователь не найден.');
    }

    let fileId;
    if (ctx.message.photo) {
      // Берем последнее (самое качественное) фото
      fileId = ctx.message.photo[ctx.message.photo.length - 1].file_id;
    } else if (ctx.message.document) {
      fileId = ctx.message.document.file_id;
    } else {
      return ctx.reply('Пожалуйста, отправьте фото или документ.');
    }

    // Получаем информацию о файле
    const file = await ctx.telegram.getFile(fileId);
    const fileUrl = `https://api.telegram.org/file/bot${process.env.TELEGRAM_BOT_TOKEN}/${file.file_path}`;

    // Загружаем файл
    const response = await axios.get(fileUrl, { responseType: 'arraybuffer' });
    const buffer = Buffer.from(response.data);

    // Создаем FormData для загрузки на сервер
    const formData = new FormData();
    formData.append('file', buffer, {
      filename: `${state.type.toLowerCase()}_${Date.now()}.${file.file_path.split('.').pop()}`
    });

    // Загружаем файл на сервер (в реальном проекте)
    // const uploadResponse = await axios.post('${process.env.UPLOAD_URL}/upload', formData);
    // const fileUrl = uploadResponse.data.url;

    // Сохраняем документ в базе данных
    await ctx.prisma.document.create({
      data: {
        userId: user.id,
        type: state.type,
        url: fileUrl, // В реальном проекте здесь будет URL загруженного файла
        verified: false
      }
    });

    // Очищаем состояние
    documentStates.delete(userId);

    await ctx.reply(`
✅ Документ успешно загружен

Тип: ${getDocumentTypeName(state.type)}
Статус: ⏳ На проверке

Мы уведомим вас, когда документ будет проверен.
    `);

    // Отправляем уведомление администраторам
    const admins = await ctx.prisma.user.findMany({
      where: { role: 'ADMIN' }
    });

    for (const admin of admins) {
      try {
        await ctx.telegram.sendMessage(admin.telegramId, `
📄 Новый документ на проверку

Пользователь: ${user.firstName} ${user.lastName}
ID: ${user.telegramId}
Тип документа: ${getDocumentTypeName(state.type)}

Используйте панель администратора для проверки:
${process.env.FRONTEND_URL}/admin/documents
        `);
      } catch (error) {
        console.error(`Ошибка при отправке уведомления админу ${admin.id}:`, error);
      }
    }
  } catch (error) {
    console.error('Ошибка при загрузке документа:', error);
    ctx.reply('Произошла ошибка при загрузке документа. Попробуйте позже.');
  }
}

module.exports = {
  handleDocuments,
  handleDocumentCallback,
  handleDocumentUpload
}; 