from typing import NewType
from uuid import UUID

from app.settings.components.core import APIModel

DeviceID = NewType("DeviceID", UUID)


class Device(APIModel):
    id: DeviceID
