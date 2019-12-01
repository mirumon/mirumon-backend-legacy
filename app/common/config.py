import logging
import sys

from databases import DatabaseURL
from loguru import logger
from starlette.config import Config

from app.common.logging import InterceptHandler, format_record
from app.common.versions import get_app_version

APP_VERSION = get_app_version()

REST_SLEEP_TIME = 0.5
REST_MAX_RESPONSE_TIME = 20.0

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)
DATABASE_URL: DatabaseURL = config("DB_CONNECTION", cast=DatabaseURL)


LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(
    handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL, "format": format_record}]
)
