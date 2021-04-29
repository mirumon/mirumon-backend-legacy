import uuid

from pydantic import BaseModel


class DeviceCommand(BaseModel):
    sync_id: uuid.UUID
    device_id: uuid.UUID
    command_type: str
    command_attributes: dict  # type: ignore
