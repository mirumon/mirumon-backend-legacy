import uuid
from typing import Optional

from pydantic import BaseModel


class SyncDeviceSystemInfoCommand(BaseModel):
    sync_id: Optional[uuid.UUID] = None
    device_id: uuid.UUID
    command_type: str = "sync_device_system_info"
    command_attributes: dict = {}
