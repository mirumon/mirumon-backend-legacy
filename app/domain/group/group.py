from typing import List, NewType
from uuid import UUID

from pydantic import BaseModel

from app.domain.device.base import Device

GroupUID = NewType("GroupUID", UUID)


class DeviceGroup(BaseModel):
    group_uid: GroupUID
    groups: List[Device]
