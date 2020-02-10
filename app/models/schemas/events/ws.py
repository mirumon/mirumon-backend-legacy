from typing import Optional

from pydantic import BaseModel

from app.models.domain.types import EventType, ResultWS
from app.models.schemas.events.base import BaseEventResponse
from app.models.schemas.events.rest import ErrorInResponse


class EventInRequestWS(BaseModel):
    method: EventType


class EventInResponseWS(BaseEventResponse):
    method: EventType
    result: Optional[ResultWS]  # noqa: WPS110
    error: Optional[ErrorInResponse]
