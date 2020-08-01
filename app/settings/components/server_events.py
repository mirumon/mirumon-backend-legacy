from typing import Callable

from fastapi import FastAPI

from app.settings.components.connections import (
    close_devices_connections,
    create_devices_connections,
)
from app.settings.components.database import close_db_connection, create_db_connection
from app.settings.components.rabbit import (
    close_rabbit_connection,
    create_rabbit_connection,
)
from app.settings.components.redis import (
    close_redis_connection,
    create_redis_connection,
)
from app.settings.environments.base import AppSettings


def create_startup_events_handler(app: FastAPI, settings: AppSettings) -> Callable:
    async def startup() -> None:  # noqa: WPS430
        create_devices_connections(app=app, settings=settings)
        await create_db_connection(app=app, settings=settings)
        await create_redis_connection(app=app, settings=settings)
        await create_rabbit_connection(app=app, settings=settings)

    return startup


def create_shutdown_events_handler(app: FastAPI) -> Callable:
    async def shutdown() -> None:  # noqa: WPS430
        await close_devices_connections(app)
        await close_rabbit_connection(app)
        await close_redis_connection(app)
        await close_db_connection(app)

    return shutdown
