from datetime import datetime
from typing import List, Optional

from app.domain.device.base import Device
from app.settings.components.core import APIModel


class OperatingSystem(APIModel):
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int
    install_date: datetime

    class Config:
        schema_extra = {
            "example": {
                "name": "Windows 10 Edu",
                "version": "1.12.12",
                "os_architecture": "amd64",
                "serial_number": "AGFNE-34GS-RYHRE",
                "number_of_users": 4,
                "install_date": "2020-07-26T00:32:16.944988",
            }
        }


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

    class Config:
        schema_extra = {
            "example": {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "online": True,
                "name": "Manjaro-Desktop",
                "domain": "mirumon.dev",
                "workgroup": None,
                "last_user": {
                    "name": "nick",
                    "fullname": "Nick Khitrov",
                    "domain": "mirumon.dev",
                },
            }
        }


class DeviceOverview(Device):
    online: bool
    name: str
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "dd8475c9-80b8-472a-a7ba-c5aeff36fb9d",
                "online": True,
                "name": "Manjaro-Desktop",
                "domain": "mirumon.dev",
                "last_user": {
                    "name": "nick",
                    "fullname": "Nick Khitrov",
                    "domain": "mirumon.dev",
                },
            }
        }
