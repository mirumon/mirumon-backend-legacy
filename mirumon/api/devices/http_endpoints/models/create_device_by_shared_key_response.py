from mirumon.api.api_model import APIModel


class CreateDeviceBySharedKeyResponse(APIModel):
    token: str
    name: str
