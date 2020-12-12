from mirumon.application.devices.device_repo import DevicesRepository
from mirumon.application.events.events_repo import EventsRepository
from mirumon.domain.devices.entities import Device
from mirumon.settings.environments.app import AppSettings


class DevicesService:
    def __init__(
        self,
        settings: AppSettings,
        devices_repo: DevicesRepository,
        events_repo: EventsRepository,
    ) -> None:
        self.settings = settings
        self.devices_repo = devices_repo
        self.events_repo = events_repo

    async def register_new_device(self) -> Device:
        device_id = Device.generate_id()
        device = Device(id=device_id)
        device_db = await self.devices_repo.create(device)
        return Device(**device_db.dict())
