from fastapi import APIRouter, Depends, HTTPException, Response
from loguru import logger
from starlette import status

from app.api.dependencies.services import get_service
from app.api.models.ws.events.types import EventTypes
from app.domain.devices.base import DeviceID
from app.services.devices.events_service import EventsService

DEVICE_UNAVAILABLE_ERROR = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
)

router = APIRouter()


@router.post(
    path="/{device_id}/shutdown",
    name="devices:shutdown",
    summary="Shutdown Device",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
async def shutdown_device(
    device_id: DeviceID,
    events_service: EventsService = Depends(get_service(EventsService)),
) -> None:
    try:
        event_id = await events_service.send_event_request(
            event_type=EventTypes.shutdown, device_id=device_id
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        await events_service.listen_event(event_id, EventTypes.shutdown)
    except RuntimeError:
        logger.debug(f"listening timeout for event:{event_id}")
        raise DEVICE_UNAVAILABLE_ERROR
