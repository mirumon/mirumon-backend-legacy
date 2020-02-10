from enum import Enum
from typing import Any, Union
from uuid import UUID

from app.models.schemas.devices.execute import ExecuteCommand

DeviceUID = UUID
SyncID = UUID

EventParams = Union[ExecuteCommand]
Result = Any
ResultWS = Any


class EventType(str, Enum):  # noqa: WPS600
    devices_list: str = "devices-list"
    detail: str = "detail"
    hardware: str = "hardware"
    software: str = "software"
    shutdown: str = "shutdown"
    execute: str = "execute"

    def __str__(self) -> str:
        return self.value  # pragma: no cover
