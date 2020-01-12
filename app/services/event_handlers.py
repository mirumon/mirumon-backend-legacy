from typing import List, Union, cast

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.common import config
from app.models.schemas.computers.details import ComputerInList
from app.models.schemas.events.rest import (
    EventInRequest,
    EventInRequestWS,
    EventInResponseWS,
    EventType,
)
from app.services.clients_manager import Client, ClientsManager
from app.services.events_manager import EventsManager


async def register_client(client: Client) -> bool:
    try:
        registration_data = await client.read_registration_data()
    except ValidationError as validation_error:
        message: Union[list, str] = validation_error.errors()
    except ValueError as value_error:
        message = str(value_error)
    else:
        message = "invalid shared token"
        if registration_data.shared_token == config.SHARED_TOKEN:
            await client.send_registration_success()
            return True

    await client.send_registration_failed(message=message)
    await client.close()
    return False


async def get_connected_clients(
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
        except (WebSocketDisconnect, ValidationError) as error:
            logger.debug(f"device client skipped in list event")
            continue
        computers.append(cast(ComputerInList, computer))
    return computers


async def process_event_from_client(client: Client, manager: EventsManager) -> None:
    event_response = await client.read_event()
    manager.set_event_response(
        sync_id=event_response.sync_id, event_response=event_response
    )


async def process_event_from_api_client(
    event_request: EventInRequestWS,
    websocket: WebSocket,
    clients_manager: ClientsManager,
    events_manager: EventsManager,
) -> None:
    if event_request.method == EventType.computers_list:
        event_payload = await get_connected_clients(clients_manager, events_manager)
    elif event_request.event_params is not None:
        device_uid = event_request.event_params.device_uid

        client = clients_manager.get_client(device_uid)
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
            f"device_uid is required param for event {event_request.method}",
            EventInRequest,
        )
    event_response = EventInResponseWS(
        method=event_request.method, event_result=event_payload
    )
    logger.debug(event_response)
    await websocket.send_text(event_response.json())
