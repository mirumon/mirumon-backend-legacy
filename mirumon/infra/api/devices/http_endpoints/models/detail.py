from typing import List, Optional

from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.api_model import APIModel


class OperatingSystem(APIModel):
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int


class DeviceUser(APIModel):
    name: str
    fullname: str
    domain: str


class DeviceDetail(APIModel):
    id: DeviceID
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None
    os: List[OperatingSystem]
