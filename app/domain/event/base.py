from typing import Any, NewType, Optional, Union
from uuid import UUID

from pydantic import validator

from app.domain.event.types import EventTypes
from app.settings.components.core import APIModel

SyncID = NewType("SyncID", UUID)

# add validator with map of `method: model`
EventParams = Union[Any]
EventResult = Union[Any]


class EventError(APIModel):
    code: int
    detail: Union[list, dict, str]


class Event(APIModel):
    sync_id: SyncID
    method: EventTypes


class EventInRequest(Event):
    params: Optional[EventParams] = None


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
