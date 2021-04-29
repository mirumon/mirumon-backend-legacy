from types import MappingProxyType
from typing import Callable, Type

from asyncpg import Connection
from fastapi import Depends
from starlette.datastructures import State

from mirumon.application.devices.devices_broker_repo import DeviceBrokerRepo
from mirumon.application.devices.devices_repo import DeviceRepository
from mirumon.application.devices.devices_socket_repo import DevicesSocketRepo
from mirumon.application.repo_protocol import Repository
from mirumon.application.users.users_repo import UsersRepository
from mirumon.infra.api.dependencies.state import get_state
from mirumon.infra.devices.device_repo_impl import DevicesRepoImpl
from mirumon.infra.devices.devices_broker_repo_impl import DevicesBrokerRepoImpl
from mirumon.infra.devices.devices_socket_repo_impl import DevicesSocketRepoImpl
from mirumon.infra.users.users_repo_impl import UsersRepositoryImplementation
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.app import AppSettings


def get_repository(  # type: ignore
    repo_type: Type[Repository],
) -> Callable[..., Repository]:
    try:
        return REPO_TYPES[repo_type]  # type: ignore
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
) -> DevicesRepoImpl:
    return DevicesRepoImpl(conn)


def _broker_repo_depends(
    state: State = Depends(get_state),
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesBrokerRepoImpl:
    return DevicesBrokerRepoImpl(
        connection=state.rabbit_conn,
        process_timeout=settings.event_timeout,
    )


def _devices_socket_repo_depends(
    state: State = Depends(get_state),
) -> DevicesSocketRepo:
    return DevicesSocketRepoImpl(state.redis_conn)


REPO_TYPES = MappingProxyType(
    {
        UsersRepository: _users_repo_depends,
        DeviceRepository: _devices_repo_depends,
        DeviceBrokerRepo: _broker_repo_depends,
        DevicesSocketRepo: _devices_socket_repo_depends,
    }
)
