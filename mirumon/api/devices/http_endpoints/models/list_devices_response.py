from mirumon.api.api_model import APIModel
from mirumon.domain.devices.entities import DeviceID


class Device(APIModel):
    id: DeviceID
    online: bool
    name: str


class ListDevicesResponse(APIModel):
    __root__: list[Device]
