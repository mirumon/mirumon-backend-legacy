from enum import Enum
from typing import Dict, List, Union

from pydantic import BaseModel

EventPayload = Union[List, Dict]


class ComputerEventType(str, Enum):  # noqa: WPS600
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


class ClientEventType(str, Enum):  # noqa: WPS600
    registration: str = "registration"
    auth: str = "auth"
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


class UserEventType(str, Enum):  # noqa: WPS600
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


class Event(BaseModel):
    type: ComputerEventType
    id: str


class EventInRequest(BaseModel):
    event: Event


class EventInResponse(BaseModel):
    event: Event
    payload: EventPayload = []


class EventInWS(BaseModel):
    event_type: UserEventType
    payload: EventPayload = []
