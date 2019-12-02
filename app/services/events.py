import asyncio
import uuid
from typing import Dict, cast

from loguru import logger
from starlette import websockets

from app.common.config import REST_MAX_RESPONSE_TIME, REST_SLEEP_TIME
from app.models.schemas.events.rest import (
    Event,
    EventInResponse,
    EventType,
    PayloadInResponse,
)
from app.services.computers import Client


class EventsManager:
    def __init__(self) -> None:
        self._events: Dict[uuid.UUID, EventInResponse] = {}
        self._asyncio_events: Dict[uuid.UUID, asyncio.Event] = {}

    def generate_event(self, event_type: EventType) -> Event:
        event_id = uuid.uuid4()
        event = Event(type=event_type, id=event_id)
        self._events[event_id] = EventInResponse(event=event)
        return Event(id=event_id, type=event_type)

    def set_event_response(self, event_id: uuid.UUID, event: EventInResponse) -> None:
        self._events[event_id] = event
        self._asyncio_events[event_id].set()

    # todo create events methods
    async def wait_event_from_client(
        self, event_id: uuid.UUID, client: Client
    ) -> PayloadInResponse:
        event = asyncio.Event()
        self._asyncio_events[event_id] = event
        response_time = REST_MAX_RESPONSE_TIME
        while not event.is_set():
            response_time -= REST_SLEEP_TIME
            try:
                await asyncio.wait_for(event.wait(), REST_SLEEP_TIME)
            except asyncio.futures.TimeoutError:
                if not client.is_connected or not response_time:
                    logger.debug("client disconnected while waiting event")
                    raise websockets.WebSocketDisconnect
        return cast(PayloadInResponse, self._events.pop(event_id).payload)

    def remove_event(self, event_id: uuid.UUID) -> None:
        self._events.pop(event_id)


_events_manager = EventsManager()


def get_events_manager() -> EventsManager:
    return _events_manager
