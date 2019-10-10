from pydantic import BaseModel

from app.schemas.status_enum import StatusEnum


class Status(BaseModel):
    status: StatusEnum
