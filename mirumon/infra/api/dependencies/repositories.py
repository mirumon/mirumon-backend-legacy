from types import MappingProxyType
from typing import Callable, Type

from asyncpg import Connection
from fastapi import Depends
from starlette.datastructures import State

from mirumon.infra.api.dependencies.state import get_state
from mirumon.infra.components.postgres.repo import PostgresRepository
from mirumon.infra.components.rabbitmq.repo import RabbitMQRepository
from mirumon.infra.repo_protocol import Repository
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.base import AppSettings


def get_repository(  # type: ignore
    repo_type: Type[Repository],
) -> Callable[..., Repository]:
    for repo, create_factory_for in REPO_TYPES.items():
        if issubclass(repo_type, repo):
            return create_factory_for(repo_type)  # type: ignore
    raise ValueError(f"{repo_type} not found in registered repos")


def _postgres_repo_deps_factory(  # type: ignore
    repo_type: Type[PostgresRepository],
) -> Callable[..., PostgresRepository]:
    def _init_repo(
        conn: Connection = Depends(_get_postgres_pool_connection),
    ) -> PostgresRepository:
        return repo_type(conn)

    return _init_repo


def _rabbit_repo_deps_factory(  # type: ignore
    repo_type: Type[RabbitMQRepository],
) -> Callable[..., RabbitMQRepository]:
    def _init_repo(
        state: State = Depends(get_state),
        settings: AppSettings = Depends(get_app_settings),
    ) -> RabbitMQRepository:
        return repo_type(
            queue=state.rabbit_queue,
            exchange=state.rabbit_exchange,
            process_timeout=settings.event_timeout,
        )

    return _init_repo


async def _get_postgres_pool_connection(
    state: State = Depends(get_state),
) -> Connection:
    async with state.postgres_pool.acquire() as conn:
        yield conn


REPO_TYPES = MappingProxyType(
    {
        PostgresRepository: _postgres_repo_deps_factory,
        RabbitMQRepository: _rabbit_repo_deps_factory,
    }
)
