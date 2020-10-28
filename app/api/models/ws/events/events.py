from typing import Any, Dict, NewType, Optional, Union
from uuid import UUID

from pydantic import validator

from app.api.models.base import APIModel
from app.api.models.ws.events.types import EventTypes, StatusTypes

EventID = NewType("EventID", UUID)
EventParams = NewType("EventParams", dict)  # type: ignore
EventResult = NewType("EventResult", Union[dict, list])  # type: ignore


class EventError(APIModel):
    code: int
    detail: Union[list, dict, str]  # type: ignore


class EventInRequest(APIModel):
    id: EventID
    method: EventTypes
    params: Optional[EventParams] = None


class EventInResponse(APIModel):
    status: StatusTypes
    id: EventID
    method: EventTypes
    result: Optional[EventResult]
    error: Optional[EventError]

    @property
    def is_success(self) -> bool:
        return self.status == StatusTypes.ok and self.result is not None

    @property
    def payload(self) -> Dict[str, Any]:  # type: ignore
        if not self.is_success:
            raise RuntimeError("event contains error")
        return self.result  # type: ignore

    @classmethod
    @validator("error", always=True)
    def check_event_or_error(  # type:ignore
        cls,
        value: Any,
        values: dict,  # type: ignore
    ) -> Optional[EventError]:
        if value is not None and values["result"] is not None:
            raise ValueError("must not provide both result and error")
        if value is None and values.get("result") is None:
            raise ValueError("must provide result or error")
        return value
