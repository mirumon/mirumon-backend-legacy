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
    sync_id: uuid.UUID
    device_id: uuid.UUID
    event_type: str = "device_software_synced"
    event_attributes: InstalledProgramsList

    @property
    def event_attributes_to_dict(self) -> dict:  # type: ignore
        return self.event_attributes.dict()
