import asyncio
from typing import Callable, Coroutine

import aio_pika
import aiojobs
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
from mirumon.infra.components.redis.pool import (
    close_redis_connection,
    create_redis_connection,
)
from mirumon.infra.devices.devices_command_handler import DeviceCommandHandler
from mirumon.settings.environments.app import AppSettings

EventHandlerType = Callable[[], Coroutine[None, None, None]]


def create_startup_events_handler(
    app: FastAPI, settings: AppSettings
) -> EventHandlerType:
    async def startup() -> None:  # noqa: WPS430
        postgres_conn = await create_postgres_connection(settings=settings)
        redis_conn = await create_redis_connection(settings=settings)
        rabbit_conn = await create_rabbit_connection(settings=settings)

        app.state.postgres_pool = postgres_conn
        app.state.redis_conn = redis_conn
        app.state.rabbit_conn = rabbit_conn

        dsn = str(settings.rabbit_dsn)
        connection: aio_pika.Connection = await aio_pika.connect(
            dsn, client_properties={"connection_name": "Read connection"}
        )

        loop = asyncio.get_event_loop()
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

        await close_rabbit_connection(app.state.rabbit_conn)
        await close_redis_connection(app.state.redis_conn)
        await close_postgres_connection(app.state.postgres_pool)

    return shutdown
