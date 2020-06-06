from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.websockets import WebSocketDisconnect

import app.services.devices.client
from app.api.dependencies.services import get_users_service, get_events_service
from app.domain.device import detail, hardware, software
from app.domain.device.detail import DeviceDetail
from app.domain.event.types import EventTypes

from app.resources import strings
from app.services.events_service import EventsService
from app.services.users.users_service import UsersService

router = APIRouter()


def _name(event: str) -> str:
    return "devices:{0}".format(event)


def _path(event: str) -> str:
    return "/{0}/{1}".format("{device_uid}", event)

@router.get(
    path="",
    response_model=List[detail.DeviceOverview],
    name=_name(EventTypes.list),
    description=strings.DEVICES_LIST_DESCRIPTION,
)
async def devices_list(
) -> List[detail.DeviceOverview]:
    pass


@router.get(
    path="",
    name=_name(EventTypes.detail),
    description=strings.DEVICE_DETAIL_DESCRIPTION,
    response_model=detail.DeviceDetail,
)
async def get_device_detail(
    # events_service: EventsService = Depends(get_events_service),
        # client: app.DeviceClient = Depends(get_avialable)
) -> detail.DeviceDetail:
    pass
#    await events_service.send_event(method=EventTypes.detail, client=client)
#
#     try:
#         payload = await events_manager.wait_event_from_client(
#             sync_id=event_payload.sync_id, client=client
#         )
#         return DeviceDetail(uid=client.device_uid, online=True, **payload)
#     except WebSocketDisconnect:
#         error_detail = (
#             strings.EVENT_NOT_SUPPORTED
#             if client.is_connected
#             else strings.DEVICE_DISCONNECTED
#         )
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
#         )


@router.get(
    path=_path(EventTypes.hardware),
    name=_name(EventTypes.hardware),
    description=strings.DEVICE_HARDWARE_DESCRIPTION,
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
    path=_path(EventTypes.software),
    name=_name(EventTypes.software),
    description=strings.DEVICE_SOFTWARE_DESCRIPTION,
    response_model=List[software.InstalledProgram],
)
async def get_device_software(
    # client: app.services.devices.client.DeviceClient = Depends(get_client),
    # events_manager: EventsManager = Depends(events_manager_retriever()),
    # sync_id: SyncID = Depends(get_new_sync_id),
) -> detail.DeviceDetail:
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
