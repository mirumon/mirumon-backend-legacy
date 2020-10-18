from fastapi import FastAPI

from app.api import routes
from app.settings.components.server_events import (
    create_shutdown_events_handler,
    create_startup_events_handler,
)
from app.settings.environments.base import AppSettings


def create_app(settings: AppSettings) -> FastAPI:
    """Create FastAPI instance with registered events."""
    app = FastAPI(**settings.fastapi_kwargs)

    app.include_router(router=routes.router)

    app.add_event_handler("startup", create_startup_events_handler(app, settings))
    app.add_event_handler("shutdown", create_shutdown_events_handler(app))
    return app
