import uuid
from typing import Optional

from pydantic import BaseModel


class ShutdownDeviceCommand(BaseModel):
    sync_id: Optional[uuid.UUID] = None
    device_id: uuid.UUID
    command_type: str = "shutdown_device"
    command_attributes: dict = {}
