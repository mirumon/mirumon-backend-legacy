from pydantic import BaseModel

from app.schemas.computers.overview import ComputerDetails


class ComputerInRegistration(BaseModel):
    mac_address: str
    name: str
    details: ComputerDetails
