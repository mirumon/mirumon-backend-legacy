import uuid
from typing import List

from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import DeviceEventsRepository
from app.domain.device.auth import DeviceAuthInRequest, DeviceAuthInResponse
from app.domain.device.detail import DeviceOverview
from app.domain.event.base import EventInRequest
from app.services.devices.gateway import DeviceClientsGateway
from app.settings.environments.base import AppSettings

_tokens = {}


class DevicesService:
    def __init__(
        self,
        settings: AppSettings,
        devices_repo: DevicesRepository,
        events_repo: DeviceEventsRepository,
        gateway: DeviceClientsGateway,
    ) -> None:
        self.settings = settings
        self.devices_repo = devices_repo
        self.events_repo = events_repo
        self.gateway = gateway

    def check_device_credentials(self, credentials: DeviceAuthInRequest) -> bool:
        return credentials.shared_key == self.settings.shared_key

    def register_new_device(self) -> DeviceAuthInResponse:
        device = self.devices_repo.create_device()
        return DeviceAuthInResponse(device_id=device.id, device_token=device.token)

    async def get_devices_overview(self) -> List[DeviceOverview]:
        pass

    async def get_device_id_by_token(self, token: str) -> uuid.UUID:
        for d_uid, d_token in _tokens.items():
            if d_token == token:
                return d_uid
        raise KeyError("device with that token not found")
