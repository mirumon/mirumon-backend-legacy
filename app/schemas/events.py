from typing import List, Dict, Union

from pydantic import BaseModel

from schemas.events import EventTypeEnum


class Event(BaseModel):
    type: EventTypeEnum
    id: str


class EventInRequest(BaseModel):
    event: Event


class EventInResponse(BaseModel):
    event: Event
    payload: Union[List, Dict]
