from typing import AsyncGenerator, Callable, Type

from asyncpg import Connection
from asyncpg.pool import Pool
from fastapi import Depends
from starlette.requests import Request

from app.db.repositories.base import BaseRepository


def _get_db_pool(request: Request) -> Pool:
    return request.app.state.pool


async def _get_pool_connection(pool: Pool = Depends(_get_db_pool),) -> Connection:
    async with pool.acquire() as conn:
        yield conn


def get_repository(repo_type: Type[BaseRepository]) -> Callable:  # type: ignore
    async def _get_repo(  # noqa: WPS430
        conn: Connection = Depends(_get_pool_connection),
    ) -> AsyncGenerator[BaseRepository, None]:
        yield repo_type(conn)

    return _get_repo
