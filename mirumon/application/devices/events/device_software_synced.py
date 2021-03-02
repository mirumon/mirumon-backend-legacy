import uuid
from typing import List, Optional

from pydantic import BaseModel


class InstalledProgram(BaseModel):
    name: str
    vendor: str
    version: str


class InstalledProgramsList(BaseModel):
    __root__: List[InstalledProgram]


class DeviceSoftwareSynced(BaseModel):
    sync_id: Optional[uuid.UUID] = None
    device_id: uuid.UUID
    event_type: str = "device_software_synced"
    event_attributes: InstalledProgramsList
