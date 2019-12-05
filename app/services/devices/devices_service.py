import uuid

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.domain.device.base import Device, DeviceID
from app.settings.environments.base import AppSettings


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
        device_id = DeviceID(uuid.uuid4())  # todo: generate in db
        # todo: add ip, mac, etc.
        device = Device(id=device_id)
        device_db = await self.devices_repo.create(device)
        return Device.parse_obj(device_db)
