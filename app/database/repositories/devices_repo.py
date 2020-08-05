import uuid
from datetime import timedelta

from app.domain.device.typing import DeviceToken
from app.settings.components.jwt import create_jwt_token
from app.settings.environments.base import AppSettings


class DevicesRepository:
    """Redis storage implementation for devices' events."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def create_device(self) -> DeviceToken:
        device_id = uuid.uuid4()
        content = {"device_id": str(device_id)}
        secret_key = self.settings.secret_key.get_secret_value()
        delta = timedelta(days=365)
        token = create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=delta
        )
        return DeviceToken(token)
