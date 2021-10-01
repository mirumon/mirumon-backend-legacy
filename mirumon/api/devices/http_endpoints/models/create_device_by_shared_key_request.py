from typing import NewType

from pydantic import SecretStr

from mirumon.api.api_model import APIModel

SharedKey = NewType("SharedKey", SecretStr)


class CreateDeviceBySharedKeyRequest(APIModel):
    name: str
    shared_key: SharedKey
