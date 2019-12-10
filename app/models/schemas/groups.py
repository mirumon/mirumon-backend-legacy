from typing import List
from uuid import UUID

from pydantic import BaseModel


class GroupInCreate(BaseModel):
    name: str
    devices: List[UUID] = []
