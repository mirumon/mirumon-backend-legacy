from pydantic import BaseModel


class ExecuteCommand(BaseModel):
    command: str


class ExecuteResult(BaseModel):
    status: str
