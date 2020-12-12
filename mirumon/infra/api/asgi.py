from fastapi import FastAPI

from mirumon.infra.api import routers
from mirumon.infra.components.server_events import (
    create_shutdown_events_handler,
    create_startup_events_handler,
)
from mirumon.settings.environments.app import AppSettings


def create_app(settings: AppSettings) -> FastAPI:
    """Create FastAPI instance with registered events."""
    app = FastAPI(**settings.fastapi_kwargs)

    app.include_router(router=routers.router)

    app.add_event_handler("startup", create_startup_events_handler(app, settings))
    app.add_event_handler("shutdown", create_shutdown_events_handler(app))
    return app
