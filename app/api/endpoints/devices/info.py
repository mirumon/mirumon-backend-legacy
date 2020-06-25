from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from starlette import status

from app.api.dependencies.services import get_devices_service
from app.api.dependencies.user_auth import check_user_scopes
from app.domain.device import detail, hardware, software
from app.domain.device.base import DeviceID
from app.domain.device.detail import DeviceDetail, DeviceOverview
from app.domain.event.types import EventTypes
from app.domain.user.scopes import UserScopes
from app.resources import strings
from app.resources.openapi_examples.devices.info import DEVICES_LIST_EXAMPLES
from app.services.devices.devices_service import DevicesService

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/{0}/{1}".format("{device_id}", event)


@router.get(
    path="",
    name="devices:list",
    description=strings.DEVICES_LIST_DESCRIPTION,
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
    response_model=List[detail.DeviceOverview],
    responses=DEVICES_LIST_EXAMPLES,
)
async def devices_list(
    devices_service: DevicesService = Depends(get_devices_service),
) -> List[DeviceOverview]:
    return await devices_service.get_devices_overview() or []


@router.get(
    path=path(EventTypes.detail),
    name=name(EventTypes.detail),
    description=strings.DEVICE_DETAIL_DESCRIPTION,
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
    response_model=DeviceDetail,
)
async def get_device_detail(
    device_id: DeviceID, devices_service: DevicesService = Depends(get_devices_service),
) -> DeviceDetail:
    await devices_service.send_event(event_type=EventTypes.detail, device_id=device_id)
    try:
        payload = await devices_service.get_event_payload(
            device_id=device_id, event_type=EventTypes.detail
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
        )

    online = await devices_service.is_device_online(device_id)
    try:
        return DeviceDetail(online=online, **payload)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="device response invalid",
        )


@router.get(
    path=path(EventTypes.hardware),
    name=name(EventTypes.hardware),
    description=strings.DEVICE_HARDWARE_DESCRIPTION,
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
    response_model=hardware.HardwareModel,
)
async def get_device_hardware(
    # client: app.services.devices.client.DeviceClient = Depends(get_client),
    # events_manager: EventsManager = Depends(events_manager_retriever()),
    # sync_id: SyncID = Depends(get_new_sync_id),
) -> hardware.HardwareModel:
    pass
    # event_payload = EventInRequest(method=EventTypes.hardware, sync_id=sync_id)
    # await client.send_event(event_payload)
    # try:
    #     return await events_manager.wait_event_from_client(
    #         sync_id=event_payload.sync_id, client=client
    #     )
    # except WebSocketDisconnect:
    #     error_detail = (
    #         strings.EVENT_NOT_SUPPORTED
    #         if client.is_connected
    #         else strings.DEVICE_DISCONNECTED
    #     )
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
    #     )


@router.get(
    path=path(EventTypes.software),
    name=name(EventTypes.software),
    description=strings.DEVICE_SOFTWARE_DESCRIPTION,
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
    response_model=List[software.InstalledProgram],
)
async def get_device_software(
    # client: app.services.devices.client.DeviceClient = Depends(get_client),
    # events_manager: EventsManager = Depends(events_manager_retriever()),
    # sync_id: SyncID = Depends(get_new_sync_id),
) -> software.InstalledProgram:
    pass
    # event_payload = EventInRequest(method=EventTypes.software, sync_id=sync_id)
    # await client.send_event(event_payload)
    # try:
    #     return await events_manager.wait_event_from_client(
    #         sync_id=event_payload.sync_id, client=client
    #     )
    # except WebSocketDisconnect:
    #     error_detail = (
    #         strings.EVENT_NOT_SUPPORTED
    #         if client.is_connected
    #         else strings.DEVICE_DISCONNECTED
    #     )
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
    #     )
