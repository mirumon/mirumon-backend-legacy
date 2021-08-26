from mirumon.domain.devices.entities import DeviceID
from mirumon.api.api_model import APIModel


class DeviceInListResponse(APIModel):
    id: DeviceID
    online: bool
    name: str
