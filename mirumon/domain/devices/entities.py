import uuid
from dataclasses import dataclass
from typing import NewType

from mirumon.domain.core.entity import Entity

DeviceID = NewType("DeviceID", uuid.UUID)


@dataclass
class Device(Entity):
    id: DeviceID

    @classmethod
    def generate_id(cls) -> DeviceID:
        return DeviceID(uuid.uuid4())
