from typing import Optional

from pydantic import BaseModel

from app.domain.events.base import BaseEventResponse
from app.domain.events.rest import ErrorInResponse
from old_app.models.domain.types import DeviceEventType, ResultWS


class EventInRequestWS(BaseModel):
    method: DeviceEventType


class EventInResponseWS(BaseEventResponse):
    method: DeviceEventType
    result: Optional[ResultWS]  # noqa: WPS110
    error: Optional[ErrorInResponse]
