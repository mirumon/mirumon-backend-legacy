from typing import Dict, List

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from app.schemas.computers.registration import ComputerInRegistration
from app.schemas.events import Event, EventInRequest, EventInResponse
from app.schemas.statuses import Status, StatusEnum


class Client:
    def __init__(self, mac_address: str, websocket: WebSocket) -> None:
        self.mac_address = mac_address
        self.websocket = websocket

    async def send_event(self, event: Event) -> None:
        await self.websocket.send_json(EventInRequest(event=event).dict())

    async def read_event(self) -> EventInResponse:
        payload = await self.websocket.receive_json()
        logger.debug(payload)
        return EventInResponse(**payload)

    @property
    async def is_connected(self) -> bool:
        return self.websocket.state == WebSocketState.CONNECTED

    def close(self, code: int = 1000) -> None:
        self.websocket.close(code)


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[str, Client] = {}

    def add_client(self, client: Client) -> None:
        self._clients[client.mac_address] = client

    def remove_client(self, client: Client) -> None:
        self._clients.pop(client.mac_address)

    def get_client(self, mac_address: str) -> Client:
        return self._clients[mac_address]

    def clients(self) -> List[Client]:
        return list(self._clients.values())


async def client_registration(websocket: WebSocket) -> Client:
    payload = await websocket.receive_json()
    try:
        computer = ComputerInRegistration(**payload)
    except ValidationError as wrong_schema_error:
        await websocket.send_json(Status(status=StatusEnum.registration_failed).dict())
        await websocket.close()
        raise WebSocketDisconnect from wrong_schema_error

    await websocket.send_json(Status(status=StatusEnum.registration_success).dict())
    return Client(mac_address=computer.mac_address, websocket=websocket)


_clients_manager = ClientsManager()


def get_clients_manager() -> ClientsManager:
    return _clients_manager
