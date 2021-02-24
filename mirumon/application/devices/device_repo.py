from mirumon.application.repositories import Repository
from mirumon.domain.devices.entities import Device, DeviceID


class DeviceDoesNotExist(Exception):
    """Raised when device was not found in infra layer."""


class DevicesRepository(Repository):
    async def create(self, device: Device) -> Device:
        raise NotImplementedError

    async def get(self, device_id: DeviceID) -> Device:
        raise NotImplementedError
