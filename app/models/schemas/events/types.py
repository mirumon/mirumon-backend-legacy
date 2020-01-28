from enum import Enum
from typing import Any, Union
from uuid import UUID

from app.models.schemas.computers.execute import ExecuteCommand

DeviceUID = UUID
SyncID = UUID

EventParams = Union[ExecuteCommand]
Result = Any
ResultWS = Any


class EventType(str, Enum):  # noqa: WPS600
    computers_list: str = "computers-list"

    details: str = "details"

    hardware: str = "hardware"
    hardware_mother: str = "hardware:motherboard"
    hardware_cpu: str = "hardware:cpu"
    hardware_gpu: str = "hardware:gpu"
    hardware_network: str = "hardware:network"
    hardware_disks: str = "hardware:disks"

    installed_programs: str = "installed-programs"

    shutdown: str = "shutdown"

    execute: str = "execute"

    def __str__(self) -> str:
        return self.value  # pragma: no cover
