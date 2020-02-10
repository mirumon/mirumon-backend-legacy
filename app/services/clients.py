from typing import Union

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketState

from app.models.domain.types import DeviceUID
from app.models.schemas.events.base import BaseEventResponse
from app.models.schemas.events.rest import EventInRequest, EventInResponse


class DeviceClient:  # noqa: WPS214
    def __init__(self, device_uid: DeviceUID, websocket: WebSocket) -> None:
        self.device_uid = device_uid
        self.websocket = websocket

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

    async def send_event(self, event: EventInRequest) -> None:
        logger.debug(f"sending event {event}")
        await self.websocket.send_text(event.json())

    async def read_event(self) -> EventInResponse:
        logger.debug("start reading event data")
        payload = await self.websocket.receive_json()
        if payload.get("result") is not None:  # fixme
            payload["result"]["uid"] = self.device_uid
            payload["result"]["online"] = True

        logger.debug(payload)
        return EventInResponse(**payload)

    async def send_error(
        self, error: Union[ValidationError, Exception], code: int
    ) -> None:
        message = error.errors() if isinstance(error, ValidationError) else str(error)
        error_payload = BaseEventResponse(
            error={"code": code, "message": message}
        ).dict()
        logger.bind(payload=error_payload).error("sending error to client:")
        await self.websocket.send_json(error_payload)
