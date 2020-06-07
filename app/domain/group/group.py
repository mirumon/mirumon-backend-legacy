from typing import List, NewType
from uuid import UUID

from pydantic import BaseModel

from app.domain.device.base import Device

GroupID = NewType("GroupID", UUID)


class DeviceGroup(BaseModel):
    group_uid: GroupID
    groups: List[Device]
