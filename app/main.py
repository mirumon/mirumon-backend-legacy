from fastapi import FastAPI

from app.api.routes import api
from app.common.config import APP_VERSION, DEBUG
from app.common.events import (
    create_shutdown_events_handler,
    create_startup_events_handler,
)
from app.services.clients_manager import ClientsManager
from app.services.events_manager import EventsManager


def get_application() -> FastAPI:
    application = FastAPI(title="Mirumon service", version=APP_VERSION, debug=DEBUG)

    application.include_router(router=api.router)

    application.add_event_handler("startup", create_startup_events_handler(application))
    application.add_event_handler(
        "shutdown", create_shutdown_events_handler(application)
    )

    application.state.clients_manager = ClientsManager()
    application.state.events_manager = EventsManager()

    return application


app = get_application()
