from aioredis import Redis
from asyncpg import Connection
from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.database.repositories.users_repo import UsersRepository
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


def get_users_repo(conn: Connection = Depends(_get_pool_connection)) -> UsersRepository:
    return UsersRepository(conn=conn)


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
