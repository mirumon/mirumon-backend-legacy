from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import parse_obj_as
from starlette import status

from app.api.dependencies.services import get_service
from app.api.models.http.devices.hardware import HardwareModel
from app.api.models.http.devices.software import InstalledProgram
from app.api.models.ws.events.types import EventTypes
from app.domain.device.base import DeviceID
from app.resources import strings
from app.services.devices.events_service import EventsService

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
    response_model=List[InstalledProgram],
)
async def get_device_software(
    device_id: DeviceID,
    events_service: EventsService = Depends(get_service(EventsService)),
) -> List[InstalledProgram]:
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
    return parse_obj_as(List[InstalledProgram], event_result)


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
    return HardwareModel.parse_obj(event_result)
