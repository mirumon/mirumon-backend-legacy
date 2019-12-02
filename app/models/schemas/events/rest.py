from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from app.models.schemas.computers import details, hardware, shutdown, software
from app.models.schemas.events.ws import WSEventType


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
    List[details.ComputerInList],
    details.ComputerDetails,
    hardware.HardwareModel,
    hardware.MotherBoardModel,
    List[hardware.NetworkAdapterModel],
    List[hardware.PhysicalDiskModel],
    List[hardware.ProcessorModel],
    List[hardware.VideoControllerModel],
    List[software.InstalledProgram],
    shutdown.Shutdown,
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
