from pydantic import BaseSettings

from mirumon.domain.core.enums import StrEnum


class AppEnvTypes(StrEnum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    """Allows to determine the current application environment."""

    app_env: AppEnvTypes = AppEnvTypes.prod

    class Config:
        env_file = ".env"
