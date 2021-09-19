from mirumon.api.api_model import APIModel


class CreateDeviceResponse(APIModel):
    token: str
    name: str
