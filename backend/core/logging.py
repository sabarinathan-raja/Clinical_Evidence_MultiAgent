
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.core.config import settings


def setup_logging():

    log_path = Path(settings.LOG_FILE)

    if not log_path.is_absolute():
        log_path = settings.database_path / log_path

    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()

    logger.setLevel(
        getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    )

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str):
    return logging.getLogger(name)
