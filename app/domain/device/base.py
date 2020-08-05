from app.api.models.base import APIModel
from app.domain.device.typing import DeviceID


class Device(APIModel):
    id: DeviceID
