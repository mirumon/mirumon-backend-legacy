from typing import Optional

from pydantic import BaseModel

from app.domain.event.base import BaseEventResponse
from app.domain.event.rest import ErrorInResponse
from app.domain.event.types import DeviceEventType
from app.domain.types import ResultWS


class EventInRequestWS(BaseModel):
    method: DeviceEventType


class EventInResponseWS(BaseEventResponse):
    method: DeviceEventType
    result: Optional[ResultWS]
    error: Optional[ErrorInResponse]
