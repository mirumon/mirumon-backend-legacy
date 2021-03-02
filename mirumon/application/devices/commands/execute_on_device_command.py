import uuid
from typing import Optional

from pydantic import BaseModel


class ExecuteOnDeviceCommand(BaseModel):
    sync_id: Optional[uuid.UUID] = None
    device_id: uuid.UUID
    command_type: str = "execute_on_device"
    command_attributes: dict = {}
