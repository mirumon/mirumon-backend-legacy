from typing import List

from fastapi import APIRouter

from app.domain.device import detail, hardware, software
from app.domain.event.types import EventTypes
from app.resources import strings

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/{0}/{1}".format("{device_uid}", event)


@router.get(
    path="",
    response_model=List[detail.DeviceOverview],
    name=name(EventTypes.list),
    description=strings.DEVICES_LIST_DESCRIPTION,
)
async def devices_list() -> List[detail.DeviceOverview]:
    pass


@router.get(
    path=path(EventTypes.detail),
    name=name(EventTypes.detail),
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
    path=path(EventTypes.hardware),
    name=name(EventTypes.hardware),
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
    path=path(EventTypes.software),
    name=name(EventTypes.software),
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
