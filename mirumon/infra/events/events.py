from typing import Any, Dict, NewType, Optional, Union
from uuid import UUID

from pydantic import validator

from mirumon.domain.core.enums import StrEnum
from mirumon.infra.api.api_model import APIModel

EventID = NewType("EventID", UUID)
EventParams = NewType("EventParams", dict)  # type: ignore
EventResult = NewType("EventResult", Union[dict, list])  # type: ignore


class StatusTypes(StrEnum):
    ok = "ok"
    error = "error"


class EventError(APIModel):
    code: int
    detail: Union[list, dict, str]  # type: ignore


class EventTypes(StrEnum):
    # system events
    error: str = "error"

    # device events
    detail: str = "detail"
    hardware: str = "hardware"
    software: str = "software"

    execute: str = "execute"
    shutdown: str = "shutdown"

    def __str__(self) -> str:
        return self.value


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
