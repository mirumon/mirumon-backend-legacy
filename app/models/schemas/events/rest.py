from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from app.models.schemas.base import BaseEventResponse, DeviceID, SyncID
from app.models.schemas.computers.details import ComputerDetails, ComputerInList
from app.models.schemas.computers.execute import ExecuteCommand, ExecuteResult
from app.models.schemas.computers.hardware import (
    HardwareModel,
    MotherBoardModel,
    NetworkAdapterModel,
    PhysicalDiskModel,
    ProcessorModel,
    VideoControllerModel,
)
from app.models.schemas.computers.shutdown import Shutdown
from app.models.schemas.computers.software import InstalledProgram


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


class Device(BaseModel):
    device_id: DeviceID


EventParams = Union[Device, ExecuteCommand]
Result = Union[
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

ResultWS = Union[
    List[ComputerInList],
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


class EventInRequest(BaseModel):
    method: EventType
    event_params: Optional[EventParams] = None
    sync_id: SyncID


class ErrorInResponse(BaseModel):
    code: int
    message: str


class EventInResponse(BaseEventResponse):
    event_result: Optional[Result]
    error: Optional[ErrorInResponse]
    sync_id: SyncID


class EventInRequestWS(BaseModel):
    method: EventType
    event_params: Optional[EventParams] = None


class EventInResponseWS(BaseEventResponse):
    method: EventType
    event_result: Optional[ResultWS]
    error: Optional[ErrorInResponse]
