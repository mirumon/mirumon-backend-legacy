import logging
import sys

from loguru import logger
from starlette.config import Config

from app.logging import InterceptHandler, format_record

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=False)

REST_SLEEP_TIME = 0.5

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(
    handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL, "format": format_record}]
)
