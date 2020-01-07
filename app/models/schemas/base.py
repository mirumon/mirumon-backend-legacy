from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, validator

DeviceID = UUID
SyncID = UUID


class BaseEventResponse(BaseModel):
    event_result: Optional[Any]
    error: Optional[Any]

    @validator("error")
    def check_event_or_error(
        cls, _: Any, values: dict, **kwargs: Any  # noqa: N805, WPS110
    ) -> dict:
        event_result = values.get("event_result")
        error = values.get("error")
        if event_result is not None and error is not None:
            raise ValueError("response must contains only event_result or error only")
        if event_result is None and error is None:
            raise ValueError("response must contains event_result or error")
        return values
