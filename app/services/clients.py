from typing import Any, Dict, List, Protocol

from loguru import logger
from starlette.websockets import WebSocket, WebSocketState

from app.models.schemas.base import DeviceID
from app.models.schemas.events.rest import EventInRequest, EventInResponse


class ErrorProto(Protocol):
    def errors(self) -> List[Dict[str, Any]]:
        """Retrieve errors that can be send to client."""


class Client:
    def __init__(self, device_id: DeviceID, websocket: WebSocket) -> None:
        self.device_id = device_id
        self.websocket = websocket

    async def send_event(self, event: EventInRequest) -> None:
        logger.debug(event)
        await self.websocket.send_text(event.json())

    async def read_event(self) -> EventInResponse:
        payload = await self.websocket.receive_json()
        logger.debug(payload)
        return EventInResponse(**payload)

    @property
    def is_connected(self) -> bool:
        return self.websocket.client_state.value == WebSocketState.CONNECTED.value

    async def close(self, code: int = 1000) -> None:
        await self.websocket.close(code)
        logger.info(
            "{0} WebSocket {1} [closed]".format(
                self.websocket.scope.get("client"), self.websocket.scope.get("raw_path")
            )
        )

    async def send_error(self, errors: List[Dict[str, Any]]) -> None:
        logger.bind(payload=errors).error("client payload error")
        await self.websocket.send_json(errors)
