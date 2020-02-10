from typing import Optional

from pydantic import BaseModel

from app.models.domain.types import DeviceEventType, ResultWS
from app.models.schemas.events.base import BaseEventResponse
from app.models.schemas.events.rest import ErrorInResponse


class EventInRequestWS(BaseModel):
    method: DeviceEventType


class EventInResponseWS(BaseEventResponse):
    method: DeviceEventType
    result: Optional[ResultWS]  # noqa: WPS110
    error: Optional[ErrorInResponse]
