from enum import Enum

from pydantic import BaseModel


class StatusEnum(str, Enum):  # noqa: WPS600
    registration_success: str = "registration_success"
    registration_failed: str = "registration_failed"
    auth_success: str = "auth_success"
    auth_failed: str = "auth_failed"


class Status(BaseModel):
    status: StatusEnum
