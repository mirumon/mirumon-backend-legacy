from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

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

    def __str__(self) -> str:
        return self.value


EventPayload = Union[List, Dict]

EventType = Union[RestEventType, WSEventType]


class Event(BaseModel):
    type: EventType
    id: UUID


class EventInRequest(BaseModel):
    event: Event


class EventInResponse(BaseModel):
    event: Event
    payload: Optional[EventPayload]  # must be optional. ClientsManager init it later
