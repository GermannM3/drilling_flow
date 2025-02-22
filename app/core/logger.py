import logging
import sys
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging(settings):
    # Добавим структурированное логирование
    config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": "{time} | {level} | {message} | {extra}",
                "level": "INFO",
                "serialize": True,
            },
            {
                "sink": "logs/error.log",
                "format": "{time} | {level} | {message} | {extra}",
                "level": "ERROR",
                "rotation": "100 MB",
                "retention": "1 month",
            }
        ],
        "extra": {
            "app_name": "DrillFlow",
            "environment": settings.ENVIRONMENT
        }
    }
    
    logger.configure(**config)
    return logger 