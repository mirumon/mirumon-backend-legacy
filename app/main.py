from fastapi import FastAPI

from app.api import routes
from app.components.config import get_app_settings
from app.components.events import (
    create_shutdown_events_handler,
    create_startup_events_handler,
)


def get_app() -> FastAPI:
    get_app_settings.cache_clear()
    settings = get_app_settings()
    app = FastAPI(**settings.fastapi_kwargs)

    app.include_router(router=routes.router)

    app.add_event_handler("startup", create_startup_events_handler(app, settings))
    app.add_event_handler("shutdown", create_shutdown_events_handler(app))
    return app


app = get_app()
