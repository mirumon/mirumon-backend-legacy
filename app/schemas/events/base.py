from typing import Dict, List, Union
from uuid import UUID

from pydantic import BaseModel

from app.schemas.events.rest import RestEventType
from app.schemas.events.ws import WSEventType

EventPayload = Union[List, Dict]

EventType = Union[RestEventType, WSEventType]


class Event(BaseModel):
    type: EventType
    id: UUID


class EventInRequest(BaseModel):
    event: Event


class EventInResponse(BaseModel):
    event: Event
    payload: EventPayload = []


class EventErrorResponse(BaseModel):
    error: Union[str, Dict, List]
