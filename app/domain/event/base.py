from typing import Any, Optional, Union

from pydantic import validator

from app.api.models.base import APIModel
from app.domain.event.types import EventTypes
from app.domain.event.typing import EventParams, EventResult, SyncID


class EventError(APIModel):
    code: int
    detail: Union[list, dict, str]  # type: ignore


class Event(APIModel):
    sync_id: SyncID
    method: EventTypes


class EventInRequest(Event):
    params: Optional[EventParams] = None


# add validator with map of `method: model`
class EventInResponse(Event):
    result: Optional[EventResult]
    error: Optional[EventError]

    @validator("error", always=True)
    def check_event_or_error(  # type:ignore
        cls, value: Any, values: dict,  # type: ignore
    ) -> Optional[EventError]:
        if value is not None and values["result"] is not None:
            raise ValueError("must not provide both result and error")
        if value is None and values.get("result") is None:
            raise ValueError("must provide result or error")
        return value
