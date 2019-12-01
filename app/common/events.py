from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.db.events import close_db_connection, connect_to_db


def create_startup_events_handler(app: FastAPI) -> Callable:
    async def startup() -> None:  # noqa: WPS430
        await connect_to_db(app)

    return startup


def create_shutdown_events_handler(app: FastAPI) -> Callable:
    @logger.catch
    async def shutdown() -> None:  # noqa: WPS430
        await close_db_connection(app)

    return shutdown
