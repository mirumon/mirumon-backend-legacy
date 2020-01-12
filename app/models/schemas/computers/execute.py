from uuid import UUID

from pydantic import BaseModel


class ExecuteCommand(BaseModel):
    device_uid: UUID
    command: str


class ExecuteResult(BaseModel):
    status: str
