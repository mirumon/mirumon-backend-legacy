from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from app.models.schemas.computers import details, hardware, shutdown, software


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

    shutdown: str = "shutdown"

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
