from typing import Protocol

from app.domain.device.typing import DeviceID


class Device(Protocol):
    id: DeviceID
