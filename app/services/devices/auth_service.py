import uuid
from datetime import timedelta

from pydantic import SecretStr, BaseModel

from app.domain.device.base import Device
from app.domain.device.typing import DeviceToken, DeviceID
from app.services.authentication.base_auth_service import AuthService
from app.settings.environments.base import AppSettings


class DeviceInToken(BaseModel):
    id: str

    class Config:
        orm_mode = True


class DevicesAuthService(AuthService):

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def is_valid_shared_key(self, shared_key: SecretStr) -> bool:
        return shared_key.get_secret_value() == self.settings.shared_key.get_secret_value()

    def create_device_token(self, device: Device) -> DeviceToken:
        content = {"device": DeviceInToken(id=str(device.id)).dict()}
        secret_key = self.settings.secret_key.get_secret_value()
        delta = timedelta(days=365)
        token = self.create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=delta
        )
        return DeviceToken(token)

    async def get_device_from_token(self, token: str) -> Device:
        try:
            content = self.get_content_from_token(
                token, self.settings.secret_key.get_secret_value()
            )
            device_payload = content.get("device")
            return DeviceInToken.parse_obj(device_payload)  # type: ignore
        except ValueError:
            raise RuntimeError
