from typing import NewType
from uuid import UUID

from pydantic import BaseModel

DeviceUID = NewType("DeviceUID", UUID)


class Device(BaseModel):
    device_uid: DeviceUID
