from typing import NewType

from app.components.core import APIModel
from app.domain.device.base import DeviceUID

DeviceToken = NewType("DeviceToken", str)


class DeviceAuthInRequest(APIModel):
    shared_token: DeviceToken


class DeviceAuthInResponse(APIModel):
    device_uid: DeviceUID
    device_token: DeviceToken
