from typing import List, Optional

from app.database.models.base import ModelDB


class OperatingSystem(ModelDB):
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int


class DeviceUser(ModelDB):
    name: str
    fullname: str
    domain: str


class DeviceInfo(ModelDB):
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None
    os: List[OperatingSystem]
