from typing import AsyncGenerator, Callable, Type

from aioredis import Redis
from asyncpg import Connection
from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.database.repositories.base_repo import BaseRepository
from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.db_pool


def _get_redis_pool(request: Request) -> Redis:
    return request.app.state.redis_pool


def _get_redis_pool_ws(websocket: WebSocket) -> Redis:
    return websocket.app.state.redis_pool


async def _get_pool_connection(pool: Pool = Depends(_get_db_pool)) -> Connection:
    async with pool.acquire() as conn:
        yield conn


def _get_db_repository(repository_type: Type[BaseRepository]) -> Callable:
    async def _get_repo(
        conn: Connection = Depends(_get_pool_connection),
    ) -> AsyncGenerator[BaseRepository, None]:
        yield repository_type(conn)

    return _get_repo


def get_devices_repo(
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesRepository:
    return DevicesRepository(settings=settings)


def get_devices_repo_ws(
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesRepository:
    return DevicesRepository(settings=settings)


def get_events_repo(
    request: Request, settings: AppSettings = Depends(get_app_settings),
) -> EventsRepository:
    state = request.app.state
    return EventsRepository(
        settings=settings, queue=state.rabbit_queue, exchange=state.rabbit_exchange
    )


def get_events_repo_ws(
    websocket: WebSocket, settings: AppSettings = Depends(get_app_settings),
) -> EventsRepository:
    state = websocket.app.state
    return EventsRepository(
        settings=settings, queue=state.rabbit_queue, exchange=state.rabbit_exchange
    )
