from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, validator

DeviceUID = UUID
SyncID = UUID


class BaseEventResponse(BaseModel):
    event_result: Optional[Any]
    error: Optional[Any]

    @validator("error", always=True)
    def check_event_or_error(
        cls, value: Any, values: dict,  # noqa: N805, WPS110
    ) -> dict:

        if value is not None and values["event_result"] is not None:
            raise ValueError("must not provide both event_result and error")
        if value is None and values.get("event_result") is None:
            raise ValueError("must provide event_result or error")
        return value
