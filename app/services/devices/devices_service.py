import uuid

from pydantic import BaseModel

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.domain.device.base import Device
from app.domain.device.typing import DeviceID
from app.settings.environments.base import AppSettings


class DeviceInCreate(BaseModel):
    id: DeviceID


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
        device_id = uuid.uuid4()
        # todo: add ip, mac, etc.
        device = DeviceInCreate(id=device_id)
        device_db = await self.devices_repo.create_device(device)
        return device_db
