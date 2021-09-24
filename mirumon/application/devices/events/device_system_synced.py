import uuid
from typing import Optional

from pydantic import BaseModel

from mirumon.application.devices.events.device_event import DeviceEvent


class OperatingSystem(BaseModel):
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int


class DeviceUser(BaseModel):
    name: str
    fullname: str
    domain: str


class SystemInfo(BaseModel):
    name: str
    os: list[OperatingSystem]
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None


class DeviceSystemSynced(DeviceEvent):
    event_id: Optional[uuid.UUID] = None
    device_id: uuid.UUID
    event_type: str = "device_system_synced"
    event_attributes: SystemInfo

    @property
    def event_attributes_to_dict(self) -> dict:  # type: ignore
        return self.event_attributes.dict()
