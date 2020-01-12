from typing import Optional, Union

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketState

from app.models.schemas.base import BaseEventResponse, DeviceUID
from app.models.schemas.events.connection import (
    RegistrationInRequest,
    RegistrationInResponse,
    StatusType,
)
from app.models.schemas.events.rest import EventInRequest, EventInResponse


class Client:  # noqa: WPS214
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
        if payload.get("event_result"):  # fixme
            payload["event_result"]["uid"] = self.device_uid
            payload["event_result"]["online"] = True

        logger.debug(payload)
        return EventInResponse(**payload)

    async def read_registration_data(self) -> RegistrationInRequest:
        logger.debug("start reading registration data")
        payload = await self.websocket.receive_json()
        return RegistrationInRequest(**payload)

    async def send_registration_success(self) -> None:
        logger.error("client registration success")
        await self.websocket.send_text(
            RegistrationInResponse(
                status=StatusType.success, device_uid=self.device_uid
            ).json()
        )

    async def send_registration_failed(
        self, message: Optional[Union[dict, list, str]] = None
    ) -> None:
        logger.error(f"client registration failed with message {message}")
        await self.websocket.send_text(
            RegistrationInResponse(status=StatusType.failed, message=message).json(
                exclude_none=True
            )
        )

    async def send_error(
        self, error: Union[ValidationError, Exception], code: int
    ) -> None:
        message = error.errors() if isinstance(error, ValidationError) else str(error)
        error_payload = BaseEventResponse(
            error={"code": code, "message": message}
        ).dict()
        logger.bind(payload=error_payload).error("sending error to client:")
        await self.websocket.send_json(error_payload)
