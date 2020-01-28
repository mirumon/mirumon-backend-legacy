from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.schemas.computers.user import User
from app.models.schemas.events.types import DeviceUID


class OperatingSystem(BaseModel):
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int
    install_date: datetime


class ComputerDetails(BaseModel):
    uid: DeviceUID
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    current_user: Optional[User] = None
    os: List[OperatingSystem]


class ComputerOverview(BaseModel):
    uid: DeviceUID
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    current_user: Optional[User] = None
