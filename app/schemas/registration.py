from pydantic import BaseModel

from app.schemas.overview import ComputerOverview


class ComputerRegistration(BaseModel):
    mac_address: str
    name: str
    overview: ComputerOverview
