from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, List, Tuple, Union

from asyncpg import Record
from asyncpg.connection import Connection
from asyncpg.pool import Pool
from asyncpg.transaction import Transaction
from loguru import logger

_FETCHER = Union[Pool, Connection]


def _log_query(query: str, query_params: Tuple[Any, ...]) -> None:
    logger.debug("query: {0}, values: {1}", query, query_params)


class BaseRepository:
    def __init__(self, pool: Pool) -> None:
        self._pool = pool
        self._fetcher: _FETCHER = pool

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[Transaction]:
        async with self._pool.acquire() as conn:
            self._fetcher = conn
            async with conn.transaction() as tr:
                yield tr
        self._fetcher = self._pool

    async def _log_and_fetch(self, query: str, *query_params: Any) -> List[Record]:
        _log_query(query, query_params)
        return await self._fetcher.fetch(query, *query_params)

    async def _log_and_fetch_row(self, query: str, *query_params: Any) -> Record:
        _log_query(query, query_params)
        return await self._fetcher.fetchrow(query, *query_params)

    async def _log_and_fetch_value(self, query: str, *query_params: Any) -> Any:
        _log_query(query, query_params)
        return await self._fetcher.fetchval(query, *query_params)

    async def _log_and_execute(self, query: str, *query_params: Any) -> None:
        _log_query(query, query_params)
        await self._fetcher.execute(query, *query_params)

    async def _log_and_execute_many(
        self, query: str, *query_params: Tuple[Any, ...]
    ) -> None:
        _log_query(query, query_params)
        await self._fetcher.executemany(query, *query_params)
