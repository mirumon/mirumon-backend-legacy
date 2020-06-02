from fastapi import FastAPI

from app.api import routes
from app.settings.environments.config import APP_VERSION, DEBUG


def get_application() -> FastAPI:
    application = FastAPI(title="Mirumon Service", version=APP_VERSION, debug=DEBUG)

    application.include_router(router=routes.router)

    application.add_event_handler("startup", create_startup_events_handler(application))
    application.add_event_handler(
        "shutdown", create_shutdown_events_handler(application)
    )

    return application


app = get_application()
