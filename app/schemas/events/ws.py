from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from app.schemas.computers.details import ComputerDetails, ComputerInList


class WSEventType(str, Enum):  # noqa: WPS600
    computers_list: str = "computers-list"
    details: str = "details"

    users: str = "users"

    system: str = "system"
    hardware: str = "hardware"
    storage: str = "storage"
    network: str = "network"

    devices: str = "devices"

    installed_programs: str = "installed-programs"
    startup_programs: str = "startup-programs"
    services: str = "services"
    processes: str = "processes"

    def __str__(self) -> str:
        return self.value


class WSComputerPayload(BaseModel):
    computer_id: str


class WSEventInRequest(BaseModel):
    event_type: WSEventType
    payload: Optional[WSComputerPayload] = None


class WSEventInResponse(BaseModel):
    event_type: WSEventType
    payload: Union[List[ComputerInList], ComputerDetails]
