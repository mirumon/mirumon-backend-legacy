from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import parse_obj_as
from starlette import status

from mirumon.application.devices.events_service import EventsService
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.services import get_service
from mirumon.infra.api.endpoints.devices.http.models.hardware import HardwareModel
from mirumon.infra.api.endpoints.devices.http.models.software import (
    ListInstalledProgram,
)
from mirumon.infra.events.events import EventTypes
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
    path=path(EventTypes.software),
    name=name(EventTypes.software),
    summary="Get Device Software",
    description=strings.DEVICES_SOFTWARE_DESCRIPTION,
    response_model=ListInstalledProgram,
)
async def get_device_software(
    device_id: DeviceID,
    events_service: EventsService = Depends(get_service(EventsService)),
) -> ListInstalledProgram:
    try:
        event_id = await events_service.send_event_request(
            event_type=EventTypes.software, device_id=device_id
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        event_result = await events_service.listen_event(
            event_id, EventTypes.software, process_timeout=10
        )
    except RuntimeError:
        logger.debug(f"listening timeout for event:{event_id}")
        raise DEVICE_UNAVAILABLE_ERROR
    return parse_obj_as(ListInstalledProgram, [item.dict() for item in event_result])


@router.get(
    path=path(EventTypes.hardware),
    name=name(EventTypes.hardware),
    summary="Get Device Hardware",
    description=strings.DEVICES_HARDWARE_DESCRIPTION,
    response_model=HardwareModel,
)
async def get_device_hardware(
    device_id: DeviceID,
    events_service: EventsService = Depends(get_service(EventsService)),
) -> HardwareModel:
    try:
        event_id = await events_service.send_event_request(
            event_type=EventTypes.hardware, device_id=device_id
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        event_result = await events_service.listen_event(event_id, EventTypes.hardware)
    except RuntimeError:
        logger.debug(f"listening timeout for event:{event_id}")
        raise DEVICE_UNAVAILABLE_ERROR
    return HardwareModel.parse_obj(event_result.dict())
