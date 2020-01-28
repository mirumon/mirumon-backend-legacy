import asyncio
import uuid
from typing import Dict, Set, cast

from loguru import logger
from starlette import websockets

from app.common.config import REST_MAX_RESPONSE_TIME, REST_SLEEP_TIME
from app.models.schemas.events.rest import EventInResponse
from app.models.schemas.events.types import Result, SyncID
from app.services.clients_manager import Client

# Used to indicate that a connection was closed abnormally
# (that is, with no close frame being sent)
# when a status code is expected.
ABNORMAL_CLOSURE = 1006
# The server is terminating the connection due to a temporary condition,
# e.g. it is overloaded and is casting off some of its clients.
TRY_AGAIN_LATER = 1013


class EventsManager:
    def __init__(self) -> None:
        self._registered_events: Set[SyncID] = set()
        self._events_responses: Dict[SyncID, EventInResponse] = {}
        self._asyncio_events: Dict[SyncID, asyncio.Event] = {}

    def register_event(self) -> SyncID:
        event_sync_id = cast(SyncID, uuid.uuid4())
        self._registered_events.add(event_sync_id)
        return event_sync_id

    def set_event_response(
        self, sync_id: SyncID, event_response: EventInResponse
    ) -> None:
        if sync_id not in self._registered_events:
            logger.error(f"unregistered event with sync_id {sync_id}")
            raise KeyError("unregistered event")
        self._events_responses[sync_id] = event_response
        logger.debug(event_response)
        self._asyncio_events[sync_id].set()

    async def wait_event_from_client(self, sync_id: SyncID, client: Client) -> Result:
        event = asyncio.Event()
        self._asyncio_events[sync_id] = event
        response_time = REST_MAX_RESPONSE_TIME
        while not event.is_set():
            response_time -= REST_SLEEP_TIME
            try:
                await asyncio.wait_for(event.wait(), REST_SLEEP_TIME)
            except asyncio.TimeoutError:
                if not client.is_connected:
                    logger.error("client disconnected while waiting event")
                    raise websockets.WebSocketDisconnect(code=ABNORMAL_CLOSURE)
                if not response_time:
                    logger.warning("response timeout while waiting event")
                    raise websockets.WebSocketDisconnect(code=TRY_AGAIN_LATER)
        return cast(Result, self.pop_event(sync_id).event_result)

    def pop_event(self, sync_id: SyncID) -> EventInResponse:
        self._registered_events.remove(sync_id)
        self._asyncio_events.pop(sync_id)
        return self._events_responses.pop(sync_id)
