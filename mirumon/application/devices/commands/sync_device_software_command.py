import uuid
from typing import Optional

from pydantic import BaseModel


class SyncDeviceSoftwareCommand(BaseModel):
    sync_id: Optional[uuid.UUID] = None
    device_id: uuid.UUID
    command_type: str = "sync_device_software"
    command_attributes: dict = {}
