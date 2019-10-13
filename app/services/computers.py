from typing import Dict, List, cast

from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.schemas.computers.overview import ComputerInList
from app.schemas.computers.registration import ComputerInRegistration
from app.schemas.events import (
    ComputerEventType,
    EventInRequest,
    EventInWS,
    UserEventType,
)
from app.schemas.statuses import Status, StatusEnum
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


async def clients_list(
    clients_manager: ClientsManager, events_manager: EventsManager
) -> List[ComputerInList]:
    computers = []
    for client in clients_manager.clients():
        event = events_manager.generate_event(ComputerEventType.details)
        await client.send_event(EventInRequest(event=event))
        computer = await events_manager.wait_event_from_client(
            event_id=event.id, client=client
        )
        computers.append(cast(ComputerInList, computer))
    return computers


async def clients_event_process(
    event: EventInWS,
    websocket: WebSocket,
    clients_manager: ClientsManager,
    events_manager: EventsManager,
) -> None:
    if event.event_type == UserEventType.computers_list:
        computers = await clients_list(clients_manager, events_manager)
        event.payload = computers
        await websocket.send_json(event)
    else:
        await websocket.send_json(event)


_clients_manager = ClientsManager()


def get_clients_manager() -> ClientsManager:
    return _clients_manager
