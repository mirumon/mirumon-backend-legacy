from typing import List, Optional

from mirumon.domain.core.event import DomainEvent, frozen_dataclass


@frozen_dataclass
class OperatingSystem:
    name: str
    version: str
    os_architecture: str
    serial_number: str
    number_of_users: int


@frozen_dataclass
class DeviceUser:
    name: str
    fullname: str
    domain: str


@frozen_dataclass
class DeviceDetail(DomainEvent):
    name: str
    os: List[OperatingSystem]
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None
