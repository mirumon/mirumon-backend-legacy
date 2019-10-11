import asyncio
import uuid
from typing import Dict, ItemsView, Optional, cast

from starlette.websockets import WebSocket

from app.config import REST_SLEEP_TIME
from app.schemas.events import EventInResponse


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[str, WebSocket] = {}
        self._events: Dict[str, Optional[EventInResponse]] = {}

    def add_client(self, *, mac_address: str, websocket: WebSocket) -> None:
        self._clients[mac_address] = websocket

    def remove_client(self, mac_address: str) -> None:
        self._clients.pop(mac_address)

    def get_client(self, mac_address: str) -> WebSocket:
        return self._clients[mac_address]

    def clients(self) -> ItemsView[str, WebSocket]:
        return self._clients.items()

    def has_connection(self, mac_address: str) -> bool:
        return mac_address in self._clients

    def generate_event(self, events: Optional[EventInResponse] = None) -> str:
        event_id = str(uuid.uuid4())
        self._events[event_id] = events
        return event_id

    def set_event_response(self, event_id: str, event: EventInResponse) -> None:
        self._events[event_id] = event

    def remove_event(self, event_id: str) -> None:
        self._events.pop(event_id)

    async def wait_event_from_client(
        self, event_id: str, mac_address: str
    ) -> EventInResponse:
        while self._events[event_id] is None:
            if not self.has_connection(mac_address=mac_address):
                self.remove_event(event_id)
                raise RuntimeError
            await asyncio.sleep(REST_SLEEP_TIME)

        return cast(EventInResponse, self._events.pop(event_id))


_manager = ClientsManager()


def get_client_manager() -> ClientsManager:
    return _manager
