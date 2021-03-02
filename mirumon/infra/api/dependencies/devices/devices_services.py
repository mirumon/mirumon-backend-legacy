from fastapi import Depends

from mirumon.application.devices.auth_service import DevicesAuthService
from mirumon.application.devices.devices_repo import DeviceRepository
from mirumon.application.devices.devices_service import DevicesService
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.app import AppSettings


def get_devices_auth_service(
    settings: AppSettings = Depends(get_app_settings),
) -> DevicesAuthService:
    return DevicesAuthService(settings=settings)


def get_devices_service(
    settings: AppSettings = Depends(get_app_settings),
    devices_repo: DeviceRepository = Depends(get_repository(DeviceRepository)),
) -> DevicesService:
    return DevicesService(settings=settings, devices_repo=devices_repo)
