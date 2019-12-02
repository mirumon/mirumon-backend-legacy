from typing import List, cast

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.models.schemas.computers.details import ComputerDetails, ComputerInList
from app.models.schemas.events.connection import Status, StatusType
from app.models.schemas.events.rest import EventInRequest
from app.models.schemas.events.ws import (
    WSEventInRequest,
    WSEventInResponse,
    WSEventType,
)
from app.services.clients import Client
from app.services.computers import ClientsManager
from app.services.events import EventsManager


async def client_registration(websocket: WebSocket) -> Client:
    payload = await websocket.receive_json()
    try:
        computer = ComputerDetails(**payload)
    except ValidationError as wrong_schema_error:
        logger.info(f"registration failed: {wrong_schema_error.json()}")
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
        except (WebSocketDisconnect, ValidationError):
            continue
        computers.append(cast(ComputerInList, computer))
    return computers


async def api_client_event_process(
    event_request: WSEventInRequest,
    websocket: WebSocket,
    clients_manager: ClientsManager,
    events_manager: EventsManager,
) -> None:
    if event_request.event_type == WSEventType.computers_list:
        event_payload: List[ComputerInList] = await clients_list(
            clients_manager, events_manager
        )
    elif event_request.payload:
        mac_address = event_request.payload.computer_id

        client = clients_manager.get_client(mac_address)
        event = events_manager.generate_event(event_request.event_type)

        await client.send_event(EventInRequest(event=event))
        event_payload = await events_manager.wait_event_from_client(  # type: ignore
            event_id=event.id, client=client
        )
    else:
        raise ValidationError(
            f"computer_id is required for event {event_request.event_type}",
            WSEventInRequest,
        )
    event_response = WSEventInResponse(
        event_type=event_request.event_type, payload=event_payload
    )
    await websocket.send_text(event_response.json())


async def process_incoming_event(client: Client, manager: EventsManager) -> None:
    event_response = await client.read_event()
    manager.set_event_response(event_id=event_response.event.id, event=event_response)


async def process_incoming_ws_event(
    websocket: WebSocket, clients_manager: ClientsManager, events_manager: EventsManager
) -> None:
    payload = await websocket.receive_json()
    logger.debug(payload)
    event = WSEventInRequest(**payload)
    await api_client_event_process(event, websocket, clients_manager, events_manager)
