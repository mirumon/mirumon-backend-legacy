from datetime import timedelta
from typing import Any, Dict

from pydantic import AnyUrl, BaseSettings, PostgresDsn, SecretStr

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


class AppSettings(BaseAppSettings):
    """
    This class enables the configuration of your FastAPI instance through the use of
    enviFronment variables. Any of the instance attributes can be overridden upon
    instantiation by either passing the desired value to the initializer, or by setting
    the corresponding environment variable. Note that assignments to variables are also
    validated, ensuring that even if you make runtime-modifications to the config, they
    should have the correct types.
    """

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Mirumon Service"
    version: str = "0.1.0"

    # Custom settings
    disable_docs: bool = False

    # Timeout settings
    rest_max_response_time: float = 5.0
    event_timeout: int = 5

    # Auth settings
    secret_key: SecretStr
    shared_key: SecretStr
    access_token_expire: timedelta = timedelta(weeks=1)

    # Infrastructure settings
    postgres_dsn: PostgresDsn
    rabbit_dsn: AnyUrl

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:  # type: ignore
        """
        This returns a dictionary of the most commonly used keyword arguments when
        initializing a FastAPI instance. If `self.disable_docs` is True, the various
        docs-related arguments are disabled, preventing your spec from being published.
        """
        fastapi_kwargs = {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
        if self.disable_docs:
            fastapi_kwargs.update(
                {"docs_url": None, "openapi_url": None, "redoc_url": None},
            )
        return fastapi_kwargs

    class Config:
        validate_assignment = True
