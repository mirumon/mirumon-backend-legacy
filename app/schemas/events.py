from typing import List, Dict, Union

from pydantic import BaseModel

from app.schemas.events_enum import EventTypeEnum


class Event(BaseModel):
    type: EventTypeEnum
    id: str


class EventInRequest(BaseModel):
    event: Event


class EventInResponse(BaseModel):
    event: Event
    payload: Union[List, Dict]
