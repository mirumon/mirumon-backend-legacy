from typing import Any, Optional

from pydantic import BaseModel, validator


class BaseEventResponse(BaseModel):
    result: Optional[Any]  # noqa: WPS110
    error: Optional[Any]

    @validator("error", always=True)
    def check_event_or_error(
        cls, value: Any, values: dict,  # noqa: N805, WPS110
    ) -> dict:
        if value is not None and values["result"] is not None:
            raise ValueError("must not provide both result and error")
        if value is None and values.get("result") is None:
            raise ValueError("must provide result or error")
        return value
