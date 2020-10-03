from fastapi import FastAPI

from app.api import routes
from app.settings.components.server_events import (
    create_shutdown_events_handler,
    create_startup_events_handler,
)
from app.settings.config import get_app_settings


def create_app() -> FastAPI:
    """Create FastAPI instance with registered events."""
    get_app_settings.cache_clear()
    settings = get_app_settings()
    app = FastAPI(**settings.fastapi_kwargs)

    app.include_router(router=routes.router)

    app.add_event_handler("startup", create_startup_events_handler(app, settings))
    app.add_event_handler("shutdown", create_shutdown_events_handler(app))
    return app
