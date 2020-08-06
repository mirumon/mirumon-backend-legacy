from app.database.models import DeviceInDB
from app.domain.device.base import Device
from app.settings.environments.base import AppSettings

storage = {}


class DevicesRepository:
    """Fake storage implementation for data from devices' events."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def create_device(self, device: Device) -> DeviceInDB:
        device_db = DeviceInDB.from_orm(device)
        storage[device.id] = device_db
        print(storage)
        return device_db
