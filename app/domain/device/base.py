from typing import NewType
from uuid import UUID

from app.domain.base import Entity

DeviceID = NewType("DeviceID", UUID)


class Device(Entity):
    id: DeviceID
