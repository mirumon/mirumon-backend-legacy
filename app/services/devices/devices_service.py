import uuid

from app.domain.device.auth import DeviceAuthInRequest, DeviceAuthInResponse
# TODO: save into database
from app.settings.environments.base import AppSettings

_tokens = {}


class DevicesService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def check_device_credentials(self, credentials: DeviceAuthInRequest):
        return credentials.shared_key == self.settings.shared_key

    def register_new_device(self):
        # TODO: repo save or error
        token = str(uuid.uuid4())
        device_id = uuid.uuid4()
        _tokens[device_id] = token
        return DeviceAuthInResponse(device_id=device_id, device_token=token)

    async def get_device_uid_by_token(self, token: str) -> uuid.UUID:
        for d_uid, d_token in _tokens.items():
            if d_token == token:
                return d_uid
        raise KeyError("device with current token not found")
