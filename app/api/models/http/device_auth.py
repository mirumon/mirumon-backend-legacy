from app.api.models.http.base import APIModel
from app.domain.device.typing import DeviceToken, SharedKey


class DeviceAuthInRequest(APIModel):
    shared_key: SharedKey


class DeviceAuthInResponse(APIModel):
    token: DeviceToken
