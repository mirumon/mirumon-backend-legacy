from typing import Any, List, Sequence, Tuple

from asyncpg import Connection
from asyncpg.protocol.protocol import Record
from loguru import logger

from mirumon.infra.repo_protocol import Repository


class PostgresRepository(Repository):
    """Postgres repository implementation."""

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    @property
    def connection(self) -> Connection:
        return self._conn

    async def _log_and_fetch(  # type: ignore
        self, query: str, *query_params: Any
    ) -> List[Record]:
        _log_query(query, query_params)
        return await self._conn.fetch(query, *query_params)

    async def _log_and_fetch_row(  # type: ignore
        self, query: str, *query_params: Any
    ) -> Record:
        _log_query(query, query_params)
        return await self._conn.fetchrow(query, *query_params)

    async def _log_and_fetch_value(  # type: ignore
        self, query: str, *query_params: Any
    ) -> Any:
        _log_query(query, query_params)
        return await self._conn.fetchval(query, *query_params)

    async def _log_and_execute(  # type: ignore
        self, query: str, *query_params: Any
    ) -> None:
        _log_query(query, query_params)
        await self._conn.execute(query, *query_params)

    async def _log_and_execute_many(  # type: ignore
        self, query: str, *query_params: Sequence[Tuple[Any, ...]]
    ) -> None:
        _log_query(query, query_params)
        await self._conn.executemany(query, *query_params)


def _log_query(query: str, query_params: Tuple[Any, ...]) -> None:  # type: ignore
    logger.debug("query: {0}, values: {1}", query, query_params)
