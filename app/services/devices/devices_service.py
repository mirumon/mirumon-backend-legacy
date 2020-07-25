from loguru import logger

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.domain.device.auth import DeviceAuthInRequest
from app.domain.device.base import Device, DeviceID
from app.domain.event.base import EventInResponse
from app.settings.components import jwt
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

    def check_device_credentials(self, credentials: DeviceAuthInRequest) -> bool:
        return credentials.shared_key == self.settings.shared_key

    async def register_new_device(self) -> str:
        return await self.devices_repo.create_device()

    async def get_registered_device_by_token(self, token: str) -> Device:
        try:
            content = jwt.get_content_from_token(token, self.settings.secret_key.get_secret_value())
            return Device(id=content["device_id"])
        except ValueError:
            raise RuntimeError

    async def set_online(self, device_id: DeviceID) -> None:
        await self.devices_repo.set_online(device_id)

    async def is_device_online(self, device_id: DeviceID) -> bool:
        return await self.devices_repo.is_online(device_id)

    async def get_event_result(self, device_id: DeviceID, event_type: str) -> dict:
        return await self.devices_repo.get_event(device_id, event_type)

    async def update_device(self, device_id: DeviceID, event: EventInResponse) -> None:
        if not self.events_repo.is_event_registered(event.sync_id):
            raise RuntimeError(f"unregistered event:{event.sync_id}")

        if event.result:
            await self.devices_repo.set_event(
                device_id, event.method, event.result.json()
            )
        else:
            logger.bind(payload=event.error.dict()).error(
                "device response contains error"
            )
            raise RuntimeError("device response contains error")
