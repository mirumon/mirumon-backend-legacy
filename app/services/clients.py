from loguru import logger
from starlette.websockets import WebSocket, WebSocketState

from app.schemas.events.rest import EventInRequest, EventInResponse


class Client:
    def __init__(self, mac_address: str, websocket: WebSocket) -> None:
        self.mac_address = mac_address
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
                self.websocket.scope["client"], self.websocket.scope["raw_path"]
            )
        )
