from typing import NewType

from pydantic import SecretStr

from app.domain.device.base import DeviceID
from app.settings.components.core import APIModel

DeviceToken = NewType("DeviceToken", str)  # for response should be str, not secret
SharedKey = NewType("SharedKey", SecretStr)


class DeviceAuthInRequest(APIModel):
    shared_key: SharedKey


class DeviceAuthInResponse(APIModel):
    device_id: DeviceID
    device_token: DeviceToken


class DeviceCredentials(APIModel):
    token: DeviceToken
