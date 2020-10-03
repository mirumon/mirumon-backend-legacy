from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError

from app.api.dependencies.services import get_service
from app.api.models.http.devices.detail import DeviceDetail
from app.api.models.ws.events.types import EventTypes
from app.resources import strings
from app.services.devices.events_service import EventsService

router = APIRouter()


@router.get(
    path="",
    name="devices:list",
    summary="Get Devices",
    description=strings.DEVICES_LIST_DESCRIPTION,
    response_model=List[DeviceDetail],
)
async def devices_list(
    events_service: EventsService = Depends(get_service(EventsService)),
) -> List[DeviceDetail]:
    events = []
    # TODO: new method for broadcast sending; gather tasks
    for device_id in events_service.gateway.client_ids:
        event_id = await events_service.send_event_request(
            event_type=EventTypes.detail, device_id=device_id
        )
        try:
            event_result = await events_service.listen_event(
                event_id, EventTypes.detail
            )
        except RuntimeError:
            logger.warning(f"timeout on event:{event_id} for device:{device_id}")
            continue

        try:
            events.append(
                DeviceDetail(id=device_id, online=True, **event_result.dict())
            )
        except ValidationError as error:
            logger.bind(payload=error.errors()).warning(
                f"validation error on event:{event_id} for device:{device_id}"
            )
    return events
