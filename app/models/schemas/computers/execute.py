from pydantic import BaseModel

from app.services.clients import DeviceID


class ExecuteCommand(BaseModel):
    device_id: DeviceID
    command: str


class ExecuteResult(BaseModel):
    status: str
