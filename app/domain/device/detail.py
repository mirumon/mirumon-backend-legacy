from datetime import datetime
from typing import List, Optional

from app.api.models.base import APIModel
from app.domain.device.base import Device


class OperatingSystem(APIModel):
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int
    install_date: datetime


class DeviceUser(APIModel):
    name: str
    fullname: str
    domain: str


class DeviceDetail(Device):
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None
    os: List[OperatingSystem]


class DeviceOverview(Device):
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None
