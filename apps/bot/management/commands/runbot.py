from django.core.management.base import BaseCommand
from bot.bot import main as run_bot
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        logger.info("Starting bot through Django command")
        try:
            run_bot()
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True) 