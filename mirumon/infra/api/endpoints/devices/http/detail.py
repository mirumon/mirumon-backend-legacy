from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import ValidationError
from starlette import status

from mirumon.application.events.events_service import EventsService
from mirumon.application.events.models import EventTypes
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.services import get_service
from mirumon.infra.api.endpoints.devices.http.models.detail import DeviceDetail
from mirumon.resources import strings

DEVICE_UNAVAILABLE_ERROR = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
)

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/{0}/{1}".format("{device_id}", event)


@router.get(
    path=path(EventTypes.detail),
    name=name(EventTypes.detail),
    summary="Get Device",
    description=strings.DEVICES_DETAIL_DESCRIPTION,
    response_model=DeviceDetail,
)
async def get_device_detail(
    device_id: DeviceID,
    events_service: EventsService = Depends(get_service(EventsService)),
) -> DeviceDetail:
    try:
        event_id = await events_service.send_event_request(
            event_type=EventTypes.detail, device_id=device_id
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        event_result = await events_service.listen_event(event_id, EventTypes.detail)
    except RuntimeError:
        logger.debug(f"listening timeout for event:{event_id}")
        raise DEVICE_UNAVAILABLE_ERROR
    try:
        return DeviceDetail(id=device_id, online=True, **event_result.dict())
    except ValidationError as error:
        logger.bind(payload=error.errors()).warning(
            f"validation error on event:{event_id} for device:{device_id}"
        )
        raise DEVICE_UNAVAILABLE_ERROR
