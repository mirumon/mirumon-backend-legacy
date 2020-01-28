from typing import List, cast

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.models.schemas.computers.details import ComputerOverview
from app.models.schemas.events.rest import (
    EventInRequest,
    EventInRequestWS,
    EventInResponseWS,
)
from app.models.schemas.events.types import EventType
from app.services.clients_manager import Client, ClientsManager
from app.services.events_manager import EventsManager


async def get_devices_list(
    clients_manager: ClientsManager, events_manager: EventsManager,
) -> List[ComputerOverview]:
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
            logger.debug(f"device client skipped in list event. error: {error}")
            continue
        computers.append(cast(ComputerOverview, computer))
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
    event_payload = await get_devices_list(clients_manager, events_manager)
    event_response = EventInResponseWS(
        method=event_request.method, event_result=event_payload
    )
    logger.debug(event_response)
    await websocket.send_text(event_response.json())
