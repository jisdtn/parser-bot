import logging
import os
from logging.handlers import TimedRotatingFileHandler


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        log_path = os.getenv("LOG_FILE", "/app/app.log")
        handler = TimedRotatingFileHandler(
            filename=log_path,
            when='midnight',
            interval=2,
            backupCount=3,
            encoding='utf-8',
            utc=True
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

