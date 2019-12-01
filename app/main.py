from fastapi import FastAPI

from app.api.routes import api
from app.common.config import APP_VERSION, DEBUG
from app.common.events import (
    create_shutdown_events_handler,
    create_startup_events_handler,
)


def get_application() -> FastAPI:
    application = FastAPI(title="Mirumon service", version=APP_VERSION, debug=DEBUG)

    application.include_router(router=api.router)

    application.add_event_handler("startup", create_startup_events_handler(application))
    application.add_event_handler(
        "shutdown", create_shutdown_events_handler(application)
    )

    return application


app = get_application()
