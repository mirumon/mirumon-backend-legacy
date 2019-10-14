from typing import Dict, List

from pydantic import BaseModel


class ComputerDetails(BaseModel):  # todo create models
    mac_address: str
    name: str
    domain: str
    workgroup: str
    current_user: Dict
    os: List


class ComputerInList(BaseModel):
    mac_address: str
    name: str
    username: str
    domain: str
    workgroup: str
