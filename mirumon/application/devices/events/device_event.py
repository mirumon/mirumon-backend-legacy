import uuid
from typing import Optional

from pydantic import BaseModel


class DeviceEvent(BaseModel):
    event_id: Optional[uuid.UUID] = uuid.uuid4()
    event_type: str
    event_attributes: BaseModel
    device_id: uuid.UUID
    correlation_id: Optional[uuid.UUID] = None
