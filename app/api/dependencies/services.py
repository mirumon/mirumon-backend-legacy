from fastapi import Depends

from app.api.dependencies.connections import get_clients_gateway
from app.api.dependencies.repositories import (
    get_devices_repo,
    get_events_repo,
    get_users_repo,
)
from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.database.repositories.users_repo import UsersRepository
from app.services.devices.auth_service import DevicesAuthService
from app.services.devices.devices_service import DevicesService
from app.services.devices.events_service import EventsService
from app.services.devices.gateway import DeviceClientsGateway
from app.services.users.users_service import UsersService
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def get_users_service(
    users_repository: UsersRepository = Depends(get_users_repo),
    settings: AppSettings = Depends(get_app_settings),
) -> UsersService:
    return UsersService(users_repo=users_repository, settings=settings)


def get_devices_auth_service(
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesAuthService:
    return DevicesAuthService(settings=settings)


def get_devices_service(
    settings: AppSettings = Depends(get_app_settings),
    devices_repo: DevicesRepository = Depends(get_devices_repo),
    events_repo: EventsRepository = Depends(get_events_repo),
) -> DevicesService:
    return DevicesService(
        settings=settings, devices_repo=devices_repo, events_repo=events_repo
    )


def get_events_service(
    settings: AppSettings = Depends(get_app_settings),
    events_repo: EventsRepository = Depends(get_events_repo),
    gateway: DeviceClientsGateway = Depends(get_clients_gateway),
) -> EventsService:
    return EventsService(settings=settings, events_repo=events_repo, gateway=gateway)
