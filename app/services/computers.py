from typing import Dict, List, cast

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.schemas.computers.details import ComputerDetails, ComputerInList
from app.schemas.events.base import EventInRequest
from app.schemas.events.connection import Status, StatusType
from app.schemas.events.ws import EventInWS, WSEventType
from app.services.clients import Client
from app.services.events import EventsManager


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[str, Client] = {}

    def add_client(self, client: Client) -> None:
        self._clients[client.mac_address] = client

    def remove_client(self, client: Client) -> None:
        self._clients.pop(client.mac_address)

    def get_client(self, mac_address: str) -> Client:
        return self._clients[mac_address]

    @property
    def clients(self) -> List[Client]:
        return list(self._clients.values())


async def client_registration(websocket: WebSocket) -> Client:
    payload = await websocket.receive_json()
    try:
        computer = ComputerDetails(**payload)
    except ValidationError as wrong_schema_error:
        logger.info(f"registration failed")
        await websocket.send_text(Status(status=StatusType.registration_failed).json())
        await websocket.close()
        raise WebSocketDisconnect from wrong_schema_error

    status = Status(status=StatusType.registration_success)
    await websocket.send_text(status.json())
    logger.info(status)
    return Client(mac_address=computer.mac_address, websocket=websocket)


async def clients_list(
    clients_manager: ClientsManager, events_manager: EventsManager
) -> List[ComputerInList]:
    computers = []
    for client in clients_manager.clients:
        event = events_manager.generate_event(WSEventType.computers_list)
        await client.send_event(EventInRequest(event=event))
        try:
            computer = await events_manager.wait_event_from_client(
                event_id=event.id, client=client
            )
        except WebSocketDisconnect:
            continue
        computers.append(cast(ComputerInList, computer))
    return computers


async def clients_event_process(
    event_ws: EventInWS,
    websocket: WebSocket,
    clients_manager: ClientsManager,
    events_manager: EventsManager,
) -> None:
    if event_ws.event_type == WSEventType.computers_list:
        computers = await clients_list(clients_manager, events_manager)
        event_ws.payload = computers
        await websocket.send_json(event_ws)


_clients_manager = ClientsManager()


def get_clients_manager() -> ClientsManager:
    return _clients_manager
