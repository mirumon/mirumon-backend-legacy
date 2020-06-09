from typing import NewType

from pydantic import SecretStr

from app.components.core import APIModel
from app.domain.device.base import DeviceID

DeviceToken = NewType("DeviceToken", str)  # for response should be str, not secret
SharedKey = NewType("SharedKey", SecretStr)


class DeviceAuthInRequest(APIModel):
    shared_key: SharedKey


class DeviceAuthInResponse(APIModel):
    device_id: DeviceID
    device_token: DeviceToken
