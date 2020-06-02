from typing import AsyncGenerator, Callable, Type

from asyncpg import Connection
from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import Request

from app.api.dependencies.settings import get_app_settings
from app.database.repositories.base_repo import BaseRepository
from app.database.repositories.users_repo import UsersRepository
from app.services.users.users_service import UsersService
from app.components.config import APPSettings


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.pool


async def _get_pool_connection(pool: Pool = Depends(_get_db_pool)) -> Connection:
    async with pool.acquire() as conn:
        yield conn


def _get_repository(repository_type: Type[BaseRepository]) -> Callable:
    async def _get_repo(
        conn: Connection = Depends(_get_pool_connection),
    ) -> AsyncGenerator[BaseRepository, None]:
        yield repository_type(conn)

    return _get_repo


def get_users_service(
    users_repository: UsersRepository = Depends(_get_repository(UsersRepository)),
        settings: APPSettings = Depends(get_app_settings)
) -> UsersService:
    return UsersService(users_repo=users_repository, settings=settings)
