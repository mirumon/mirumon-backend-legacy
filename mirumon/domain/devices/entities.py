import uuid
from dataclasses import dataclass
from typing import NewType

from mirumon.domain.core.entity import Entity

DeviceID = NewType("DeviceID", uuid.UUID)


@dataclass
class Device(Entity):
    id: DeviceID
    name: str
    properties: dict[str, dict]  # type: ignore

    @classmethod
    def generate_id(cls) -> DeviceID:
        return DeviceID(uuid.uuid4())

    # TODO: models
    def get_hardware(self):  # type: ignore
        return self.properties.get("hardware")

    def get_software(self):  # type: ignore
        return self.properties.get("software")

    def get_system(self):  # type: ignore
        return self.properties.get("system")
