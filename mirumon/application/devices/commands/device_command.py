import uuid
from typing import Optional

from pydantic import BaseModel


class DeviceCommand(BaseModel):
    command_id: uuid.UUID = uuid.uuid4()
    command_type: str
    command_attributes: dict  # type: ignore
    device_id: uuid.UUID
    correlation_id: Optional[uuid.UUID] = None
