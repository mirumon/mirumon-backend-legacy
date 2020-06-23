from typing import AsyncGenerator, Callable, Type

from asyncpg import Connection
from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import Request

from app.database.repositories.base_repo import BaseRepository
from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository, EventsService
from app.database.repositories.users_repo import UsersRepository
from app.services.devices.devices_service import DevicesService
from app.services.users.users_service import UsersService
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.db_pool


def _get_connections(request: Request) -> dict:
    """Connections state for websockets for devices."""
    return request.app.state.connections


async def _get_pool_connection(pool: Pool = Depends(_get_db_pool)) -> Connection:
    async with pool.acquire() as conn:
        yield conn


def _get_db_repository(repository_type: Type[BaseRepository]) -> Callable:
    async def _get_repo(
        conn: Connection = Depends(_get_pool_connection),
    ) -> AsyncGenerator[BaseRepository, None]:
        yield repository_type(conn)

    return _get_repo


def get_events_repo() -> EventsRepository:
    return EventsRepository()


def get_users_service(
    users_repository: UsersRepository = Depends(_get_db_repository(UsersRepository)),
    settings: AppSettings = Depends(get_app_settings),
) -> UsersService:
    return UsersService(users_repo=users_repository, settings=settings)


def get_devices_service(
    settings: AppSettings = Depends(get_app_settings),
    devices_repo: DevicesRepository = Depends(get_events_repo),
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesService:
    return DevicesService(settings=settings)


def get_events_service(
    settings: AppSettings = Depends(get_app_settings),
) -> EventsService:
    return EventsService(settings=settings)
