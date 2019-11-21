from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from app.schemas.computers.details import ComputerDetails, ComputerInList
from app.schemas.computers.execute import ExecuteResult
from app.schemas.computers.hardware import (
    HardwareModel,
    MotherBoardModel,
    NetworkAdapterModel,
    PhysicalDiskModel,
    ProcessorModel,
    VideoControllerModel,
)
from app.schemas.computers.shutdown import Shutdown
from app.schemas.computers.software import InstalledProgram
from app.schemas.events.ws import WSEventType


class RestEventType(str, Enum):  # noqa: WPS600
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
        return self.value


PayloadInResponse = Union[
    ComputerInList,
    ComputerDetails,
    HardwareModel,
    MotherBoardModel,
    List[NetworkAdapterModel],
    List[PhysicalDiskModel],
    List[ProcessorModel],
    List[VideoControllerModel],
    List[InstalledProgram],
    Shutdown,
    ExecuteResult,
]

EventType = Union[RestEventType, WSEventType]


class Event(BaseModel):
    type: EventType
    id: UUID


class EventInRequest(BaseModel):
    event: Event
    payload: Optional[Union[Dict, List]] = None


class EventInResponse(BaseModel):
    event: Event
    # fixme. must be optional. ClientsManager init it later
    payload: Optional[PayloadInResponse]
