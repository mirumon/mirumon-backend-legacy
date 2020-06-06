import uuid

from app.components.config import APPSettings
from app.domain.device.auth import DeviceAuthInRequest, DeviceAuthInResponse

# TODO: save into database
_tokens = {}


class DevicesService:
    def __init__(self, settings: APPSettings) -> None:
        self.settings = settings

    def check_device_credentials(self, credentials: DeviceAuthInRequest):
        return credentials.shared_token == self.settings.shared_key

    def register_new_device(self):
        # TODO: repo save or error
        token = str(uuid.uuid4())
        device_uid = uuid.uuid4()
        _tokens[device_uid] = token
        return DeviceAuthInResponse(device_uid=device_uid, device_token=token)

    async def get_device_uid_by_token(self, token: str) -> uuid.UUID:
        for d_uid, d_token in _tokens.items():
            if d_token == token:
                return d_uid
        raise KeyError("device with current token not found")
