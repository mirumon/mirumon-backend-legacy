from typing import List, cast

from loguru import logger
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from app.models.domain.types import DeviceEventType
from app.models.schemas.devices.detail import DeviceOverview
from app.models.schemas.events.rest import EventInRequest
from app.services.clients_manager import ClientsManager
from app.services.events_manager import EventsManager


async def get_devices_list(
    clients_manager: ClientsManager, events_manager: EventsManager,
) -> List[DeviceOverview]:
    devices = []

    for client in clients_manager.clients:
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
            devices.append(DeviceOverview(uid=client.device_uid, online=True, **device))
    return devices
