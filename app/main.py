from fastapi import FastAPI

from app.api import routes
from app.components.config import get_app_settings


def get_app() -> FastAPI:
    get_app_settings.cache_clear()
    settings = get_app_settings()
    app = FastAPI(**settings.fastapi_kwargs)

    app.include_router(router=routes.router)

    # app.add_event_handler("startup", create_startup_events_handler(application))
    # app.add_event_handler(
    #     "shutdown", create_shutdown_events_handler(application)
    # )
    return app


app = get_app()
