import uuid
from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from app.domain.core.model import DomainModel

DeviceID = NewType("DeviceID", UUID)


@dataclass
class Device(DomainModel):
    id: DeviceID

    @classmethod
    def generate_id(cls) -> DeviceID:
        return DeviceID(uuid.uuid4())
