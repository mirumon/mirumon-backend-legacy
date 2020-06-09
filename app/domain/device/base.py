from typing import NewType
from uuid import UUID

from pydantic import BaseModel

DeviceID = NewType("DeviceID", UUID)


class Device(BaseModel):
    id: DeviceID
