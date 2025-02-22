import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command from user {update.effective_user.id}")
    try:
        await update.message.reply_text('Привет! Я бот DrillFlow. Чем могу помочь?')
        logger.info("Successfully sent start message")
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}", exc_info=True)

def main():
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        logger.info(f"Starting bot with token: {token[:5]}...")
        
        application = Application.builder().token(token).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_error_handler(error_handler)
        
        logger.info("Bot initialized, starting polling...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)

if __name__ == '__main__':
    main() 