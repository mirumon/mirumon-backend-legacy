from pydantic import BaseModel

from app.domain.device.typing import DeviceID


class BaseModelDB(BaseModel):
    class Config:
        orm_mode = True


class DeviceInDB(BaseModelDB):
    id: DeviceID
