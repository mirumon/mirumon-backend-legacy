from typing import List, Optional

from pydantic import BaseModel

from app.models.schemas.computers.user import User


class OperatingSystem(BaseModel):
    caption: str
    version: str
    build_number: str
    os_architecture: str
    serial_number: str
    product_type: str
    number_of_users: int
    install_date: str


class ComputerDetails(BaseModel):
    mac_address: str
    name: str
    domain: str
    workgroup: Optional[str] = None
    current_user: User
    os: List[OperatingSystem]


class ComputerInList(BaseModel):
    mac_address: str
    name: str
    username: str
    domain: str
    workgroup: Optional[str] = None
