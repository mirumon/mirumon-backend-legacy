from app.database.repositories.devices_repo import DevicesRepository
from app.database.repositories.events_repo import EventsRepository
from app.domain.device.auth import DeviceAuthInRequest, DeviceToken
from app.domain.device.base import Device
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

    async def register_new_device(self) -> DeviceToken:
        return await self.devices_repo.create_device()

    async def get_registered_device_by_token(self, token: str) -> Device:
        try:
            content = jwt.get_content_from_token(
                token, self.settings.secret_key.get_secret_value()
            )
            return Device(id=content["device_id"])
        except ValueError:
            raise RuntimeError
