from typing import Union, Dict

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketState

from app.components.config import APPSettings
from app.domain.event.base import BaseEventResponse
from app.domain.event.rest import EventInRequest, EventInResponse
from old_app.models.domain.types import DeviceUID


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


class DevicesService:
    def __init__(self, settings: APPSettings) -> None:
        self.settings = settings
        self._clients: Dict[DeviceUID, DeviceClient] = {}

    def add_client(self, client: DeviceClient) -> None:
        self._clients[client.device_uid] = client

    def remove_client(self, client: DeviceClient) -> None:
        self._clients.pop(client.device_uid)

    def get_client(self, device_uid: DeviceUID) -> DeviceClient:
        return self._clients[device_uid]

    async def get_devices_list(
        clients_manager: ClientsManager, events_manager: EventsManager,
    ) -> List[DeviceOverview]:
        devices = []

        for client in list(self._clients.values()):
            sync_id = events_manager.register_event()
            await client.send_event(
                EventInRequest(method=DeviceEventType.list, sync_id=sync_id)
            )
            try:
                device = await events_manager.wait_event_from_client(
                    sync_id=sync_id, client=client
                )
            except (WebSocketDisconnect, ValidationError) as error:
                logger.debug(f"device client skipped in list event. error: {error}")
                continue
            else:
                devices.append(
                    DeviceOverview(uid=client.device_uid, online=True, **device)
                )
        return devices


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[DeviceUID, DeviceClient] = {}
