import asyncio
import uuid
from typing import Dict, Optional, Union, List

from starlette.websockets import WebSocket

from app.config import REST_SLEEP_TIME
from app.schemas.events import EventInResponse


class ClientsManager:
    _websockets: Dict[str, WebSocket] = {}
    _events: Dict[str, Optional[Union[List, Dict]]] = {}

    def add_client(self, *, mac_address: str, websocket: WebSocket) -> None:
        self._websockets[mac_address] = websocket

    def remove_client(self, mac_address: str) -> None:
        del self._websockets[mac_address]

    def get_client(self, mac_address: str) -> WebSocket:
        return self._websockets[mac_address]

    def get_all_clients(self):
        return self._websockets.items()

    def has_connection(self, mac_address: str) -> bool:
        return mac_address in self._websockets

    def generate_event(self, payload: Optional[Union[List, Dict]] = None) -> str:
        event_id = str(uuid.uuid4())
        self._events[event_id] = payload
        return event_id

    def set_event_response(self, event_id: str, payload: Union[List, Dict]) -> None:
        self._events[event_id] = payload

    def remove_event(self, event_id: str) -> None:
        del self._events[event_id]

    async def wait_event_from_client(
        self, event_id: str, mac_address: str
    ) -> EventInResponse:
        while self._events[event_id] is None:
            if not self.has_connection(mac_address=mac_address):
                self.remove_event(event_id)
                raise RuntimeError
            await asyncio.sleep(REST_SLEEP_TIME)
        return self._events.pop(event_id)


_manager = ClientsManager()


def get_client_manager() -> ClientsManager:
    return _manager
