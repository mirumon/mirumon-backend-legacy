from typing import Callable, Coroutine

from fastapi import FastAPI

from mirumon.infra.components.connections import (
    close_devices_connections,
    create_devices_connections,
)
from mirumon.infra.components.postgres.pool import (
    close_postgres_connection,
    create_postgres_connection,
)
from mirumon.infra.components.rabbitmq.pool import (
    close_rabbit_connection,
    create_rabbit_connection,
)
from mirumon.settings.environments.base import AppSettings

EventHandlerType = Callable[[], Coroutine[None, None, None]]


def create_startup_events_handler(
    app: FastAPI, settings: AppSettings
) -> EventHandlerType:
    async def startup() -> None:  # noqa: WPS430
        create_devices_connections(app=app, settings=settings)
        await create_postgres_connection(app=app, settings=settings)
        await create_rabbit_connection(app=app, settings=settings)

    return startup


def create_shutdown_events_handler(app: FastAPI) -> EventHandlerType:
    async def shutdown() -> None:  # noqa: WPS430
        await close_devices_connections(app)
        await close_rabbit_connection(app)
        await close_postgres_connection(app)

    return shutdown
