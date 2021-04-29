import uuid
from dataclasses import dataclass
from typing import NewType

from mirumon.domain.core.entity import Entity

DeviceID = NewType("DeviceID", uuid.UUID)


@dataclass
class Device(Entity):
    id: DeviceID
    name: str
    properties: dict[str, dict]

    @classmethod
    def generate_id(cls) -> DeviceID:
        return DeviceID(uuid.uuid4())
