from typing import Callable

from fastapi import FastAPI

from app.components.config import APPSettings
from app.components.database import (
    close_db_connection,
    create_db_connection,
    create_superuser,
)


def create_startup_events_handler(app: FastAPI, settings: APPSettings) -> Callable:
    async def startup() -> None:  # noqa: WPS430
        await create_db_connection(app=app, settings=settings)
        await create_superuser(app=app, settings=settings)

    return startup


def create_shutdown_events_handler(app: FastAPI) -> Callable:
    async def shutdown() -> None:  # noqa: WPS430
        await close_db_connection(app)

    return shutdown
