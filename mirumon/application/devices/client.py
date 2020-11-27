from typing import Dict, List

from loguru import logger
from starlette.websockets import WebSocket, WebSocketState

from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.events.events import EventInRequest, EventInResponse


class DeviceClient:
    def __init__(self, device_id: DeviceID, websocket: WebSocket) -> None:
        self.device_id = device_id
        self.websocket = websocket

    async def send_event(self, event: EventInRequest) -> None:
        logger.debug("sending event {0} to device:{1}", event, self.device_id)
        await self.websocket.send_text(event.json())

    async def read_event(self) -> EventInResponse:
        logger.debug("start reading event data from device:{0}", self.device_id)
        payload = await self.websocket.receive_text()
        logger.debug("event payload from device:{0}\n{1}", self.device_id, payload)
        return EventInResponse.parse_raw(payload)

    async def send_error(self, error: Dict[str, str]) -> None:
        error_payload = {"errors": [error]}
        logger.bind(payload=error_payload).error(
            "sending error to device:{0}",
            self.device_id,
        )
        await self.websocket.send_json(error_payload)

    async def send_errors(self, errors: List[Dict[str, str]]) -> None:
        error_payload = {"errors": errors}
        logger.bind(payload=error_payload).error(
            "sending errors to device:{0}",
            self.device_id,
        )
        await self.websocket.send_json(error_payload)

    @property
    def is_connected(self) -> bool:
        return self.websocket.client_state.value == WebSocketState.CONNECTED.value

    async def close(self, code: int = 1000) -> None:
        await self.websocket.close(code)
        client = self.websocket.scope.get("client", "")
        path = self.websocket.scope.get("raw_path", "")
        logger.info("{0} WebSocket {1} [closed]", client, path)
