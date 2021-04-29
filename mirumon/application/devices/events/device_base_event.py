import uuid

from pydantic import BaseModel


class DeviceBaseEvent(BaseModel):
    sync_id: uuid.UUID
    device_id: uuid.UUID
    event_type: str = "base_event"
    event_attributes: BaseModel

    @property
    def event_attributes_to_dict(self):
        return self.event_attributes.dict()
