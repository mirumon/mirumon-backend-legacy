from uuid import UUID

from pydantic import BaseModel


class ExecuteCommand(BaseModel):
    device_id: UUID
    command: str


class ExecuteResult(BaseModel):
    status: str
