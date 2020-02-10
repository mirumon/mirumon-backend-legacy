from typing import Optional

from pydantic import BaseModel

from app.models.domain.types import EventParams, EventType, Result, SyncID
from app.models.schemas.events.base import BaseEventResponse


class RegistrationInRequest(BaseModel):
    shared_token: str


class RegistrationInResponse(BaseModel):
    device_token: str


class EventInRequest(BaseModel):
    method: EventType
    event_params: Optional[EventParams] = None
    sync_id: SyncID


class ErrorInResponse(BaseModel):
    code: int
    message: str


class EventInResponse(BaseEventResponse):
    result: Optional[Result]  # noqa: WPS110
    error: Optional[ErrorInResponse]
    sync_id: SyncID
