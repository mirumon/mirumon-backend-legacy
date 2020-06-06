from typing import Any, NewType, Optional, Union
from uuid import UUID

from pydantic import validator

from app.components.core import APIModel
from app.domain.event.types import EventTypes

SyncID = NewType("SyncID", UUID)
EventParams = Union[Any]
EventResult = Union[Any]


class Event(APIModel):
    sync_d: SyncID
    method: EventTypes


class EventInRequest(Event):
    event_params: Optional[EventParams] = None


class EventError(APIModel):
    code: int
    message: str


class EventInResponse(Event):
    result: Optional[EventResult]
    error: Optional[EventError]

    @validator("error", always=True)
    def check_event_or_error(
        cls, value: Any, values: dict,  # noqa: N805, WPS110
    ) -> dict:
        if value is not None and values["result"] is not None:
            raise ValueError("must not provide both result and error")
        if value is None and values.get("result") is None:
            raise ValueError("must provide result or error")
        return value
