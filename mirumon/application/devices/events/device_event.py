import uuid
from typing import Optional

from pydantic import BaseModel


class DeviceEvent(BaseModel):
    sync_id: Optional[uuid.UUID]
    device_id: uuid.UUID
    event_type: str
    event_attributes: BaseModel

    @property
    def event_attributes_to_dict(self) -> dict:  # type: ignore
        return self.event_attributes.dict()
