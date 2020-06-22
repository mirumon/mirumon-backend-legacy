from typing import Callable

from fastapi import FastAPI

from app.settings.components.database import (
    close_db_connection,
    create_db_connection,
)
from app.settings.environments.base import AppSettings


def create_startup_events_handler(app: FastAPI, settings: AppSettings) -> Callable:
    async def startup() -> None:  # noqa: WPS430
        await create_db_connection(app=app, settings=settings)

    return startup


def create_shutdown_events_handler(app: FastAPI) -> Callable:
    async def shutdown() -> None:  # noqa: WPS430
        await close_db_connection(app)

    return shutdown
