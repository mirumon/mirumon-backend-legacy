from app.database.models.base import ModelDB
from app.database.repositories.protocols.base import PostgresRepository
from app.domain.devices.device import Device, DeviceID

_storage = {}  # type: ignore


class DeviceInDB(ModelDB):
    id: DeviceID


class DevicesRepository(PostgresRepository):
    """Fake storage implementation for devices info."""

    async def create(self, device: Device) -> Device:
        _storage[device.id] = device
        return device

    async def get(self, device_id: DeviceID) -> Device:
        return _storage[device_id]
