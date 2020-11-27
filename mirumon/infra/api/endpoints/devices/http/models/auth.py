from typing import NewType

from pydantic import SecretStr

from mirumon.infra.api.api_model import APIModel

DeviceToken = NewType("DeviceToken", str)  # for response should be str, not secret
SharedKey = NewType("SharedKey", SecretStr)


class DeviceAuthInRequest(APIModel):
    shared_key: SharedKey


class DeviceAuthInResponse(APIModel):
    token: DeviceToken
