import uuid
from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from mirumon.domain.core.entity import Entity

DeviceID = NewType("DeviceID", UUID)


@dataclass
class Device(Entity):
    id: DeviceID

    @classmethod
    def generate_id(cls) -> DeviceID:
        return DeviceID(uuid.uuid4())
