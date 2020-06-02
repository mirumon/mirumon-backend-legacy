import logging
import sys

from databases import DatabaseURL
from loguru import logger
from starlette.config import Config
from starlette.datastructures import Secret

from app.settings.components.logger import InterceptHandler, format_record
from old_app.common.versions import get_app_version

APP_VERSION = get_app_version()

JWT_TOKEN_TYPE: str = "Bearer"


config = Config(".env")

REST_MAX_RESPONSE_TIME: float = config(
    "REST_MAX_RESPONSE_TIME", cast=float, default=5.0  # noqa: WPS432
)
REST_SLEEP_TIME: float = config(
    "REST_SLEEP_TIME", cast=float, default=0.5
)  # noqa: WPS432

DEBUG: bool = config("DEBUG", cast=bool, default=False)
DATABASE_URL: DatabaseURL = config("DB_CONNECTION", cast=DatabaseURL)
SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)
SHARED_TOKEN: str = config("SHARED_TOKEN", cast=str)

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(
    handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL, "format": format_record}]
)

# Initial superuser configs
FIRST_SUPERUSER: str = config("FIRST_SUPERUSER", default="")
FIRST_SUPERUSER_PASSWORD: Secret = config(
    "FIRST_SUPERUSER_PASSWORD", cast=Secret, default=""
)
INITIAL_SUPERUSER_SCOPES = (
    "users:execute",
    "users:read",
    "admin:view",
    "admin:edit",
)
