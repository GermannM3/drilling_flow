import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bot import handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Вставьте свой токен Telegram-бота
    TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", handlers.start))
    dispatcher.add_handler(CommandHandler("help", handlers.help_command))
    dispatcher.add_handler(CommandHandler("profile", handlers.profile))
    dispatcher.add_handler(CommandHandler("support", handlers.support))
    dispatcher.add_handler(CommandHandler("order", handlers.create_order))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handlers.echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main() 