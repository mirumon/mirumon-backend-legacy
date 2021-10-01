import uuid
from typing import Any, Optional

from pydantic import BaseModel, validator

from mirumon.domain.core.enums import StrEnum


class DeviceAgentRequest(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    method: str
    params: Optional[dict] = None  # type: ignore
    correlation_id: Optional[uuid.UUID] = None


class StatusTypes(StrEnum):
    ok = "ok"
    error = "error"


class DeviceAgentResponse(BaseModel):
    id: uuid.UUID
    status: StatusTypes
    method: str
    correlation_id: Optional[uuid.UUID] = None
    result: Optional[dict]  # type: ignore
    error: Optional[dict]  # type: ignore

    @property
    def is_success(self) -> bool:
        return self.status == StatusTypes.ok and self.result is not None

    @classmethod
    @validator("error", always=True)
    def check_event_or_error(  # type:ignore
        cls,
        value: Any,
        values: dict,  # type: ignore
    ) -> Optional[dict]:  # type: ignore
        if value is not None and values["result"] is not None:
            raise ValueError("must not provide both result and error")
        if value is None and values.get("result") is None:
            raise ValueError("must provide result or error")
        return value
