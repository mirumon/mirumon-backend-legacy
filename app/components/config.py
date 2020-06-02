"""
https://github.com/dmontagu/fastapi-utils/blob/master/fastapi_utils/api_settings.py
"""

from typing import Any, Dict, Tuple

from databases import DatabaseURL
from pydantic import BaseSettings
from starlette.datastructures import Secret

from app.components.version import get_app_version


class APPSettings(BaseSettings):
    """
    This class enables the configuration of your FastAPI instance through the use of environment variables.
    Any of the instance attributes can be overridden upon instantiation by either passing the desired value to the
    initializer, or by setting the corresponding environment variable.
    Attribute `xxx_yyy` corresponds to environment variable `API_XXX_YYY`. So, for example, to override
    `openapi_prefix`, you would set the environment variable `API_OPENAPI_PREFIX`.
    Note that assignments to variables are also validated, ensuring that even if you make runtime-modifications
    to the config, they should have the correct types.
    """

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Mirumon Service"
    version: str = get_app_version()

    # Custom settings
    disable_docs: bool = True

    # Timeout settings
    rest_max_response_time: float = 5.0

    # Auth settings
    secret_key: Secret
    shared_key: Secret
    jwt_token_type: str = "Bearer"

    # Database settings
    database_url: DatabaseURL

    # First user credentials
    first_superuser: str
    first_superuser_password: Secret
    initial_superuser_scopes: Tuple[str] = (
        "users:execute",
        "users:read",
        "admin:view",
        "admin:edit",
    )

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        """
        This returns a dictionary of the most commonly used keyword arguments when initializing a FastAPI instance
        If `self.disable_docs` is True, the various docs-related arguments are disabled, preventing your spec from being
        published.
        """
        fastapi_kwargs: Dict[str, Any] = {
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
                {"docs_url": None, "openapi_url": None, "redoc_url": None}
            )
        return fastapi_kwargs

    class Config:
        env_prefix = "api_"
        validate_assignment = True
