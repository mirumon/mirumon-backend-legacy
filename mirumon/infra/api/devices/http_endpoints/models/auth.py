from typing import NewType

from pydantic import SecretStr

from mirumon.infra.api.api_model import APIModel

SharedKey = NewType("SharedKey", SecretStr)


class DeviceCreateRequest(APIModel):
    name: str


class DeviceAuthInRequest(APIModel):
    shared_key: SharedKey
    name: str


class DeviceAuthInResponse(APIModel):
    token: str
    name: str
