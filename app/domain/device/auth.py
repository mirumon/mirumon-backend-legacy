from typing import NewType

from pydantic import SecretStr

from app.components.core import APIModel
from app.domain.device.base import DeviceID

DeviceToken = NewType("DeviceToken", SecretStr)
SharedKey = NewType("SharedKey", SecretStr)


class DeviceAuthInRequest(APIModel):
    shared_key: SharedKey


class DeviceAuthInResponse(APIModel):
    device_uid: DeviceID
    device_token: DeviceToken
