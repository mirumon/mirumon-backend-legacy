from typing import List, Dict

from pydantic import BaseModel


class ComputerDetails(BaseModel):  # todo create models
    name: str
    domain: str
    workgroup: str
    users: List
    current_user: Dict
    logon_users: List
    os: List
    enviroment: List


class ComputerInList(BaseModel):
    name: str
    username: str
    domain: str
