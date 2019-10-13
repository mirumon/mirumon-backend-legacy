import asyncio
import uuid
from typing import Dict, List, Optional, Union, cast

from starlette import websockets

from app.schemas.events import ComputerEventType, Event, EventInResponse, UserEventType
from app.services.computers import Client


class EventsManager:
    def __init__(self) -> None:
        self._events: Dict[str, Optional[EventInResponse]] = {}
        self._asyncio_events: Dict[str, asyncio.Event] = {}

    def generate_event(
        self, event_type: Union[ComputerEventType, UserEventType]
    ) -> Event:
        event_id = str(uuid.uuid4())
        event = Event(type=event_type, id=event_id)
        self._events[event_id] = EventInResponse(event=event)
        return Event(id=event_id, type=event_type)

    def set_event_response(self, event_id: str, event: EventInResponse) -> None:
        self._events[event_id] = event
        self._asyncio_events[event_id].set()

    # todo create events methods
    async def wait_event_from_client(
        self, event_id: str, client: Client
    ) -> Union[List, Dict]:
        event = asyncio.Event()
        self._asyncio_events[event_id] = event
        await event.wait()
        if not client.is_connected:
            raise websockets.WebSocketDisconnect
        return cast(EventInResponse, self._events.pop(event_id)).payload

    def remove_event(self, event_id: str) -> None:
        self._events.pop(event_id)


async def process_incoming_event(client: Client, manager: EventsManager) -> None:
    response = await client.read_event()
    manager.set_event_response(event_id=response.event.id, event=response)


_events_manager = EventsManager()


def get_events_manager() -> EventsManager:
    return _events_manager
