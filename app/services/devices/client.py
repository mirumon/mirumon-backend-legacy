from typing import Union

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketState

from app.domain.device.base import DeviceID
from app.domain.event.base import EventError, EventInRequest, EventInResponse


class DeviceClient:
    def __init__(self, device_uid: DeviceID, websocket: WebSocket) -> None:
        self.device_uid = device_uid
        self.websocket = websocket

    async def send_event(self, event: EventInRequest) -> None:
        logger.debug("sending event {0} to {1}", event, self.device_uid)
        await self.websocket.send_text(event.json())

    async def read_event(self) -> EventInResponse:
        logger.debug("start reading event data from {0}", self.device_uid)
        payload = await self.websocket.receive_json()
        logger.bind(payload=payload).debug("event payload from {0}", self.device_uid)
        return EventInResponse(**payload)

    async def send_error(
        self, error: Union[ValidationError, Exception], code: int
    ) -> None:
        message = error.errors() if isinstance(error, ValidationError) else str(error)
        error_payload = EventInResponse(
            error=EventError(code=code, message=message)
        ).dict()
        logger.bind(payload=error_payload).error(
            "sending error to client {0}", self.device_uid
        )
        await self.websocket.send_json(error_payload)

    @property
    def is_connected(self) -> bool:
        return self.websocket.client_state.value == WebSocketState.CONNECTED.value

    async def close(self, code: int = 1000) -> None:
        await self.websocket.close(code)
        client = self.websocket.scope.get("client")
        path = self.websocket.scope.get("raw_path")
        logger.info("{0} WebSocket {1} [closed]", client, path)
