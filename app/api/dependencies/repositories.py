from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import HTTPConnection, Request

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.database.repositories.users_repo import UsersRepository
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.db_pool


def get_users_repo(pool: Pool = Depends(_get_db_pool)) -> UsersRepository:
    return UsersRepository(pool=pool)


def get_devices_repo(
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesRepository:
    return DevicesRepository(settings=settings)


def get_events_repo(
    conn: HTTPConnection, settings: AppSettings = Depends(get_app_settings),
) -> EventsRepository:
    state = conn.app.state
    return EventsRepository(
        settings=settings, queue=state.rabbit_queue, exchange=state.rabbit_exchange
    )
