import uuid
from json import JSONDecodeError
from typing import List

from pydantic import ValidationError

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.domain.device.auth import DeviceAuthInRequest, DeviceAuthInResponse
from app.domain.device.base import Device, DeviceID
from app.domain.device.detail import DeviceOverview
from app.domain.event.base import SyncID, EventInResponse
from app.domain.event.types import EventTypes
from app.services.devices.client import DeviceClient
from app.services.devices.gateway import DeviceClientsGateway
from app.settings.environments.base import AppSettings


class DevicesService:
    def __init__(
        self,
        settings: AppSettings,
        devices_repo: DevicesRepository,
        events_repo: EventsRepository,
        gateway: DeviceClientsGateway,
    ) -> None:
        self.settings = settings
        self.devices_repo = devices_repo
        self.events_repo = events_repo
        self.gateway = gateway

    def check_device_credentials(self, credentials: DeviceAuthInRequest) -> bool:
        return credentials.shared_key == self.settings.shared_key

    def register_new_device(self) -> DeviceAuthInResponse:
        # todo jwt token
        device = self.devices_repo.create_device()
        return DeviceAuthInResponse(device_id=device.id, device_token=device.token)

    async def get_registered_device_by_token(self, token: str) -> Device:
        return self.devices_repo.get_device_by_token(token)

    def add_client(self, client: DeviceClient) -> None:
        self.gateway.add_client(client)

    def remove_client(self, client: DeviceClient):
        self.gateway.remove_client(client)

    async def send_event(self, device_id: DeviceID, event_type: str) -> None:
        await self.events_repo.register_event(device_id=device_id, event_type=event_type)

    async def update_device(self, device_id, event: EventInResponse):
        if not self.events_repo.is_event_registered(event.sync_id):
            raise RuntimeError(f"unregistered event:{event.sync_id}")

        await self.devices_repo.set_event(device_id, event.method, event.result.json())

    async def get_devices_overview(self) -> List[DeviceOverview]:
        pass

