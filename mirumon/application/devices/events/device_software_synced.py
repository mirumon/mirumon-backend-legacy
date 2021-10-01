import uuid
from typing import List

from pydantic import BaseModel

from mirumon.application.devices.events.device_event import DeviceEvent


class InstalledProgram(BaseModel):
    name: str
    vendor: str
    version: str


class InstalledProgramsList(BaseModel):
    installed_programs: List[InstalledProgram]


class DeviceSoftwareSynced(DeviceEvent):
    event_id: uuid.UUID
    device_id: uuid.UUID
    event_type: str = "device_software_synced"
    event_attributes: InstalledProgramsList
