from mirumon.application.devices.devices_repo import DeviceRepository
from mirumon.domain.devices.entities import Device
from mirumon.settings.environments.app import AppSettings


class DevicesService:
    def __init__(
        self,
        settings: AppSettings,
        devices_repo: DeviceRepository,
    ) -> None:
        self.settings = settings
        self.devices_repo = devices_repo

    async def register_new_device(self, name: str) -> Device:
        device_id = Device.generate_id()
        device = Device(id=device_id, name=name, properties={})
        device_db = await self.devices_repo.create(device)
        return Device(**device_db.dict())
