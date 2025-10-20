import logging
import os
from logging.handlers import RotatingFileHandler
from pydantic import BaseModel

LOGGER_NAME: str = "adhan_api"

class LogConfig(BaseModel):
    """Logging configuration for the Adhan API server."""

    LOGGER_NAME: str = LOGGER_NAME
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Ensure logs directory exists
    LOG_FILE_PATH: str = "logs/app.log"
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    # Logging configuration
    version: int = 1
    disable_existing_loggers: bool = False

    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }

    handlers: dict = {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "encoding": "utf-8",
            "maxBytes": 100 * 1024 * 1024,  # 100 MB
            "backupCount": 5,  # keep 5 old log files
        },
    }

    loggers: dict = {
        LOGGER_NAME: {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    }

    @staticmethod
    def get_logger():
        """Return the configured logger."""
        return logging.getLogger(LOGGER_NAME)
