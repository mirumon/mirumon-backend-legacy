from app.components.core import APIModel


class DeviceAuthInRequest(APIModel):
    shared_token: str


class DeviceAuthInResponse(APIModel):
    device_token: str
