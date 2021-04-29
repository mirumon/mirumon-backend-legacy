import asyncio
from typing import Callable, Coroutine

import aiojobs
from aio_pika import connect
from fastapi import FastAPI

from mirumon.application.devices.device_socket_manager import socket_manager
from mirumon.infra.components.postgres.pool import (
    close_postgres_connection,
    create_postgres_connection,
)
from mirumon.infra.components.rabbitmq.pool import (
    close_rabbit_connection,
    create_rabbit_connection,
)
from mirumon.infra.devices.devices_command_handler import DeviceCommandHandler
from mirumon.settings.environments.app import AppSettings

EventHandlerType = Callable[[], Coroutine[None, None, None]]


def create_startup_events_handler(
    app: FastAPI, settings: AppSettings
) -> EventHandlerType:
    async def startup() -> None:  # noqa: WPS430
        # TODO: refactor to return conns and init state in server events
        await create_postgres_connection(app=app, settings=settings)
        await create_rabbit_connection(app=app, settings=settings)

        loop = asyncio.get_event_loop()
        dsn = str(settings.rabbit_dsn)
        connection = await connect(dsn)
        handler = DeviceCommandHandler(loop, connection, socket_manager)
        scheduler = await aiojobs.create_scheduler()
        app.state.scheduler = scheduler
        app.state.connection = connection

        app.state.job = await scheduler.spawn(handler.start())

    return startup


def create_shutdown_events_handler(app: FastAPI) -> EventHandlerType:
    async def shutdown() -> None:  # noqa: WPS430
        await app.state.job.close()
        await app.state.scheduler.close()
        await app.state.connection.close()
        await close_rabbit_connection(app)
        await close_postgres_connection(app)

    return shutdown
