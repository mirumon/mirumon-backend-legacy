from typing import List

from fastapi import APIRouter, Depends
from loguru import logger

from app.api.dependencies.services import get_events_service
from app.domain.device.detail import DeviceOverview
from app.domain.event.types import EventTypes
from app.resources import strings
from app.services.devices.events_service import EventsService

router = APIRouter()


@router.get(
    path="",
    name="devices:list",
    description=strings.DEVICES_LIST_DESCRIPTION,
    response_model=List[DeviceOverview],
)
async def devices_list(
    events_service: EventsService = Depends(get_events_service),
) -> List[DeviceOverview]:
    events = []
    for device_id in events_service.gateway.client_ids:
        sync_id = await events_service.send_event_request(
            event_type=EventTypes.list, device_id=device_id, params=[]
        )
        try:
            event = await events_service.listen_event(sync_id)
        except RuntimeError:
            logger.debug(f"timeout on event:{sync_id} for device:{device_id}")
        else:
            events.append(DeviceOverview(online=True, **event.result))  # type: ignore

    return events
