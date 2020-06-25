from typing import List

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.domain.device.auth import DeviceAuthInRequest, DeviceAuthInResponse
from app.domain.device.base import Device, DeviceID
from app.domain.device.detail import DeviceOverview
from app.domain.event.base import EventInResponse
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

    def register_new_device(self) -> DeviceAuthInResponse:
        # todo jwt token
        device = self.devices_repo.create_device()
        return DeviceAuthInResponse(device_id=device.id, device_token=device.token)

    async def get_registered_device_by_token(self, token: str) -> Device:
        return self.devices_repo.get_device_by_token(token)

    async def set_online(self, device_id: DeviceID) -> None:
        await self.devices_repo.set_online(device_id)

    async def is_device_online(self, device_id: DeviceID) -> bool:
        return await self.devices_repo.is_online(device_id)

    async def send_event(self, device_id: DeviceID, event_type: str) -> None:
        await self.events_repo.register_event(
            device_id=device_id, event_type=event_type
        )

    async def get_event_payload(self, device_id: DeviceID, event_type: str) -> dict:
        return await self.devices_repo.get_event(device_id, event_type)

    async def update_device(self, device_id, event: EventInResponse) -> None:
        if not self.events_repo.is_event_registered(event.sync_id):
            raise RuntimeError(f"unregistered event:{event.sync_id}")

        if event.result:
            await self.devices_repo.set_event(
                device_id, event.method, event.result.json()
            )
        else:
            raise RuntimeError("device response contains error")

    async def get_devices_overview(self) -> List[DeviceOverview]:
        pass
