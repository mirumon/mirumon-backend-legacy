from enum import Enum
from typing import Optional

from pydantic import BaseModel
from typing_extensions import Literal

from app.services.clients_manager import DeviceID


class ConnectionEventType(str, Enum):  # noqa: WPS600
    registration: str = "registration"
    auth: str = "auth"

    def __str__(self) -> str:
        return self.value


class StatusType(str, Enum):  # noqa: WPS600
    success: str = "success"
    failed: str = "failed"

    def __str__(self) -> str:
        return self.value


class RegistrationInRequest(BaseModel):
    connection_type: Literal[ConnectionEventType.registration]
    shared_token: str


class RegistrationInResponse(BaseModel):
    status: StatusType
    device_id: Optional[DeviceID]


class AuthInRequest(BaseModel):
    connection_type: Literal[ConnectionEventType.auth]
    shared_token: str
    device_id: DeviceID


class AuthInResponse(BaseModel):
    status: StatusType
