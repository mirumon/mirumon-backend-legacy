from enum import Enum

from pydantic import BaseModel


class ConnectionEventType(str, Enum):  # noqa: WPS600
    registration: str = "registration"
    auth: str = "auth"

    def __str__(self) -> str:
        return self.value


class StatusType(str, Enum):  # noqa: WPS600
    registration_success: str = "registration-success"
    registration_failed: str = "registration-failed"
    auth_success: str = "auth-success"
    auth_failed: str = "auth-failed"


class Status(BaseModel):
    status: StatusType

    # mypy complains about invalid overriding signature
    def __str__(self) -> str:  # type: ignore
        return self.status
