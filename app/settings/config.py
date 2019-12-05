"""Environments configuration and reading for usage in any part of application."""
from functools import lru_cache
from typing import Dict, Type

from app.settings.environments.base import AppEnvTypes, AppSettings, BaseAppSettings
from app.settings.environments.development import DevAppSettings
from app.settings.environments.production import ProdAppSettings
from app.settings.environments.testing import TestAppSettings

environments: Dict[str, Type[AppSettings]] = {
    AppEnvTypes.prod: ProdAppSettings,
    AppEnvTypes.dev: DevAppSettings,
    AppEnvTypes.test: TestAppSettings,
}


@lru_cache()
def get_app_settings() -> AppSettings:
    """
    This function returns a cached instance of the AppSettings object.

    Returns certain settings depending on the set APP_ENV environment variable.

    Caching is used to prevent re-reading the environment every time  the API settings
    are used in an endpoint. If you want to change an environment variable and reset
    the cache (e.g., during testing), this can be done using the `lru_cache` instance
    method `get_api_settings.cache_clear()`.
    """
    app_env = BaseAppSettings().app_env
    config = environments[app_env]
    return config()
