from typing import List, Optional

from mirumon.api.api_model import APIModel


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


class SystemAttributes(APIModel):
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    last_user: Optional[DeviceUser] = None
    os: List[OperatingSystem]


class GetDeviceSystemResponse(APIModel):
    os_type: str = "windows"  # todo implement other os types
    system_attributes: SystemAttributes
