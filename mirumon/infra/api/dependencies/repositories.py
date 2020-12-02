from types import MappingProxyType
from typing import Callable, Type

from asyncpg import Connection
from fastapi import Depends
from starlette.datastructures import State

from mirumon.application.devices.device_repo import DevicesRepository
from mirumon.application.events.events_repo import EventsRepository
from mirumon.application.repo_protocol import Repository
from mirumon.application.users.users_repo import UsersRepository
from mirumon.infra.api.dependencies.state import get_state
from mirumon.infra.devices.device_repo_impl import DevicesRepositoryImplementation
from mirumon.infra.events.events_repo_impl import EventsRepositoryImplementation
from mirumon.infra.users.users_repo_impl import UsersRepositoryImplementation
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.base import AppSettings


def get_repository(  # type: ignore
    repo_type: Type[Repository],
) -> Callable[..., Repository]:
    try:
        return REPO_TYPES[repo_type]
    except KeyError:
        raise RuntimeError(f"{repo_type} not found in registered repos for DI")


async def _get_postgres_pool_connection(
    state: State = Depends(get_state),
) -> Connection:
    async with state.postgres_pool.acquire() as conn:
        yield conn


def _users_repo_depends(
    conn: Connection = Depends(_get_postgres_pool_connection),
) -> UsersRepositoryImplementation:
    return UsersRepositoryImplementation(conn)


def _devices_repo_depends(
    conn: Connection = Depends(_get_postgres_pool_connection),
) -> DevicesRepositoryImplementation:
    return DevicesRepositoryImplementation(conn)


def _events_repo_depends(
    state: State = Depends(get_state),
    settings: AppSettings = Depends(get_app_settings),
) -> EventsRepositoryImplementation:
    return EventsRepositoryImplementation(
        queue=state.rabbit_queue,
        exchange=state.rabbit_exchange,
        process_timeout=settings.event_timeout,
    )


REPO_TYPES = MappingProxyType(
    {
        UsersRepository: _users_repo_depends,
        DevicesRepository: _devices_repo_depends,
        EventsRepository: _events_repo_depends,
    }
)
