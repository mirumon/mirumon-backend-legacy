from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.models.domain.groups import Group


class Device(BaseModel):
    id: UUID
    name: str
    mac_addr: str
    groups: List[Group]
    data: dict
