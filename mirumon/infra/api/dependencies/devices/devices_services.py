from fastapi import Depends

from mirumon.application.devices.auth_service import DevicesAuthService
from mirumon.application.devices.device_repo import DevicesRepository
from mirumon.application.devices.devices_service import DevicesService
from mirumon.application.devices.gateway import DeviceClientsManager
from mirumon.application.events.events_repo import EventsRepository
from mirumon.application.events.events_service import EventsService
from mirumon.infra.api.dependencies.devices.connections import (
    get_device_clients_manager,
)
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.app import AppSettings


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
