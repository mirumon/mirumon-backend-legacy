"""Environments configuration and reading for usage in any part of application."""
from functools import lru_cache
from typing import Dict, Type

from mirumon.settings.environments.app import AppSettings
from mirumon.settings.environments.base import AppEnvTypes, BaseAppSettings
from mirumon.settings.environments.development import DevAppSettings
from mirumon.settings.environments.production import ProdAppSettings
from mirumon.settings.environments.testing import TestAppSettings

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
