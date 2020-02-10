from typing import List, cast

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from app.models.domain.types import EventType
from app.models.schemas.devices.details import ComputerOverview
from app.models.schemas.events.rest import EventInRequest
from app.services.clients_manager import ClientsManager
from app.services.events_manager import EventsManager


async def get_devices_list(
    clients_manager: ClientsManager, events_manager: EventsManager,
) -> List[ComputerOverview]:
    computers = []

    for client in clients_manager.clients:
        sync_id = events_manager.register_event()
        await client.send_event(
            EventInRequest(method=EventType.devices_list, sync_id=sync_id)
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
