import uuid
from typing import List, cast

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.common import config
from app.models.schemas.computers.details import ComputerInList
from app.models.schemas.events.connection import (
    RegistrationInRequest,
    RegistrationInResponse,
    StatusType,
)
from app.models.schemas.events.rest import (
    EventInRequest,
    EventInRequestWS,
    EventInResponseWS,
    EventType,
)
from app.services.clients import Client
from app.services.clients_manager import ClientsManager
from app.services.events_manager import EventsManager


async def _close_connection_with_error(websocket: WebSocket) -> None:
    await websocket.send_text(
        RegistrationInResponse(status=StatusType.failed).json(exclude_none=True)
    )
    await websocket.close()
    raise WebSocketDisconnect


async def client_registration(websocket: WebSocket) -> Client:
    payload = await websocket.receive_json()
    try:
        registration_data = RegistrationInRequest(**payload)
    except ValidationError as wrong_schema_error:
        logger.info(f"validation error: {wrong_schema_error.json()}")
        await _close_connection_with_error(websocket)

    if registration_data.shared_token != config.SHARED_TOKEN:
        logger.info(
            f"registration failed! shared token: {registration_data.shared_token}"
        )
        await _close_connection_with_error(websocket)

    device_id = uuid.uuid4()
    registration_success = RegistrationInResponse(
        status=StatusType.success, device_id=device_id
    )
    logger.info(f"registration success! generated device_id: {device_id}")
    await websocket.send_text(registration_success.json())
    return Client(device_id=device_id, websocket=websocket)


async def clients_list(
    clients_manager: ClientsManager, events_manager: EventsManager
) -> List[ComputerInList]:
    computers = []
    for client in clients_manager.clients:
        sync_id = events_manager.register_event()
        await client.send_event(
            EventInRequest(method=EventType.computers_list, sync_id=sync_id)
        )
        try:
            computer = await events_manager.wait_event_from_client(
                sync_id=sync_id, client=client
            )
        except (WebSocketDisconnect, ValidationError):
            continue
        computers.append(cast(ComputerInList, computer))
    return computers


async def api_client_event_process(
    event_request: EventInRequestWS,
    websocket: WebSocket,
    clients_manager: ClientsManager,
    events_manager: EventsManager,
) -> None:
    if event_request.method == EventType.computers_list:
        event_payload = await clients_list(clients_manager, events_manager)
    elif event_request.event_params is not None:
        device_id = event_request.event_params.device_id

        client = clients_manager.get_client(device_id)
        sync_id = events_manager.register_event()

        await client.send_event(
            EventInRequest(
                method=event_request.method,
                event_params=event_request.event_params,
                sync_id=sync_id,
            )
        )
        event_payload = await events_manager.wait_event_from_client(  # type: ignore
            sync_id=sync_id, client=client
        )
    else:
        raise ValidationError(
            f"device_id is required param for event {event_request.method}",
            EventInRequest,
        )
    event_response = EventInResponseWS(event_result=event_payload)
    await websocket.send_text(event_response.json())


async def process_incoming_event(client: Client, manager: EventsManager) -> None:
    event_response = await client.read_event()
    manager.set_event_response(
        sync_id=event_response.sync_id, event_response=event_response
    )
