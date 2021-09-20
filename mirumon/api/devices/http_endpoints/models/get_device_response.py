from mirumon.api.api_model import APIModel
from mirumon.domain.devices.entities import DeviceID


class GetDeviceResponse(APIModel):
    id: DeviceID
    online: bool
    name: str
