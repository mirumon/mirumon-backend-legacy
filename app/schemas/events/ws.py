from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from app.schemas.computers.details import ComputerDetails, ComputerInList
from app.schemas.computers.hardware import (
    HardwareModel,
    MotherBoardModel,
    NetworkAdapterModel,
    PhysicalDiskModel,
    ProcessorModel,
    VideoControllerModel,
)
from app.schemas.computers.software import InstalledProgram


class WSEventType(str, Enum):  # noqa: WPS600
    computers_list: str = "computers-list"
    details: str = "details"

    hardware: str = "hardware"
    hardware_mother: str = "hardware:motherboard"
    hardware_cpu: str = "hardware:cpu"
    hardware_gpu: str = "hardware:gpu"
    hardware_network: str = "hardware:network"
    hardware_disks: str = "hardware:disks"

    installed_programs: str = "installed-programs"

    def __str__(self) -> str:
        return self.value


class WSComputerPayload(BaseModel):
    computer_id: str


class WSEventInRequest(BaseModel):
    event_type: WSEventType
    payload: Optional[WSComputerPayload] = None


class WSEventInResponse(BaseModel):
    event_type: WSEventType
    payload: Union[
        List[ComputerInList],
        ComputerDetails,
        HardwareModel,
        MotherBoardModel,
        List[NetworkAdapterModel],
        List[PhysicalDiskModel],
        List[ProcessorModel],
        List[VideoControllerModel],
        List[InstalledProgram],
    ]
