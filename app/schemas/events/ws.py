from enum import Enum
from typing import Dict, List, Union

from pydantic import BaseModel

EventPayload = Union[List, Dict]


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


class EventInWS(BaseModel):
    event_type: WSEventType
    payload: EventPayload
