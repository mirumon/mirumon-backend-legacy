from typing import Union

from loguru import logger
from starlette.websockets import WebSocket, WebSocketState

from app.schemas.events import EventInRequest, EventInResponse, EventInWS


class Client:
    def __init__(self, mac_address: str, websocket: WebSocket) -> None:
        self.mac_address = mac_address
        self.websocket = websocket

    async def send_event(self, event: Union[EventInRequest, EventInWS]) -> None:
        await self.websocket.send_json(event.dict())

    async def read_event(self) -> EventInResponse:
        payload = await self.websocket.receive_json()
        logger.debug(payload)
        return EventInResponse(**payload)

    @property
    def is_connected(self) -> bool:
        return self.websocket.state == WebSocketState.CONNECTED

    async def close(self, code: int = 1000) -> None:
        await self.websocket.close(code)
