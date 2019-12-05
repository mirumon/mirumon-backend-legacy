from fastapi import Depends

from app.api.dependencies.devices.connections import get_device_clients_manager
from app.api.dependencies.repositories import get_repository
from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.services.devices.auth_service import DevicesAuthService
from app.services.devices.devices_service import DevicesService
from app.services.devices.events_service import EventsService
from app.services.devices.gateway import DeviceClientsManager
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def get_devices_auth_service(
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesAuthService:
    return DevicesAuthService(settings=settings)


def get_devices_service(
    settings: AppSettings = Depends(get_app_settings),
    devices_repo: DevicesRepository = Depends(get_repository(DevicesRepository)),
    events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> DevicesService:
    return DevicesService(
        settings=settings, devices_repo=devices_repo, events_repo=events_repo
    )


def get_events_service(
    events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
    gateway: DeviceClientsManager = Depends(get_device_clients_manager),
) -> EventsService:
    return EventsService(events_repo=events_repo, gateway=gateway)
