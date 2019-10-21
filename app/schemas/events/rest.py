from enum import Enum
from typing import Dict, List, Union, Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.events.ws import WSEventType


class RestEventType(str, Enum):  # noqa: WPS600
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
