from enum import Enum
from typing import Any, Union
from uuid import UUID

from app.models.schemas.devices.execute import ExecuteCommand

DeviceUID = UUID
SyncID = UUID

EventParams = Union[ExecuteCommand]
Result = Any
ResultWS = Any


class DeviceEventType(str, Enum):  # noqa: WPS600
    list: str = "list"
    detail: str = "detail"
    hardware: str = "hardware"
    software: str = "software"
    execute: str = "execute"
    shutdown: str = "shutdown"

    def __str__(self) -> str:
        return self.value  # pragma: no cover
