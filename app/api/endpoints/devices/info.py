from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.api.dependencies.services import get_events_service
from app.domain.device.detail import DeviceDetail
from app.domain.device.hardware import HardwareModel
from app.domain.device.software import InstalledProgram
from app.domain.device.typing import DeviceID
from app.domain.event.types import EventTypes
from app.resources import strings
from app.services.devices.events_service import EventsService

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/{0}/{1}".format("{device_id}", event)


@router.get(
    path=path(EventTypes.detail),
    name=name(EventTypes.detail),
    description=strings.DEVICE_DETAIL_DESCRIPTION,
    response_model=DeviceDetail,
)
async def get_device_detail(
    device_id: DeviceID, events_service: EventsService = Depends(get_events_service),
) -> DeviceDetail:
    try:
        sync_id = await events_service.send_event_request(
            event_type=EventTypes.detail, device_id=device_id, params=[]
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        event = await events_service.listen_event(sync_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
        )
    return DeviceDetail(online=True, **event.result)  # type: ignore


@router.get(
    path=path(EventTypes.software),
    name=name(EventTypes.software),
    description=strings.DEVICE_SOFTWARE_DESCRIPTION,
    response_model=List[InstalledProgram],
)
async def get_device_software(
    device_id: DeviceID, events_service: EventsService = Depends(get_events_service)
) -> List[InstalledProgram]:
    try:
        sync_id = await events_service.send_event_request(
            event_type=EventTypes.software, device_id=device_id, params=[]
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        event = await events_service.listen_event(sync_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
        )
    return [InstalledProgram.parse_obj(item) for item in event.result]  # type: ignore


@router.get(
    path=path(EventTypes.hardware),
    name=name(EventTypes.hardware),
    description=strings.DEVICE_HARDWARE_DESCRIPTION,
    response_model=HardwareModel,
)
async def get_device_hardware(
    device_id: DeviceID, events_service: EventsService = Depends(get_events_service)
) -> HardwareModel:
    try:
        sync_id = await events_service.send_event_request(
            event_type=EventTypes.hardware, device_id=device_id, params=[]
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        event = await events_service.listen_event(sync_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
        )
    return HardwareModel.parse_obj(event.result)
