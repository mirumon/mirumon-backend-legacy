from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies.user_auth import check_user_scopes
from app.domain.device import detail, hardware, software
from app.domain.event.types import EventTypes
from app.domain.user.scopes import UserScopes
from app.resources import strings

DEVICE_NOT_FOUND = "The device was not found"

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/{0}/{1}".format("{device_uid}", event)


@router.get(
    path="",
    name=name(EventTypes.list),
    description=strings.DEVICES_LIST_DESCRIPTION,
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
    response_model=List[detail.DeviceOverview],
    responses={
        200: {
            "description": "Available devices for user",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "dd8475c9-80b8-472a-a7ba-c5aeff36fb9d",
                            "online": True,
                            "name": "Manjaro-Desktop",
                            "domain": "mirumon.dev",
                            "last_user": {
                                "name": "nick",
                                "fullname": "Nick Khitrov",
                                "domain": "mirumon.dev",
                            },
                        },
                        {
                            "id": "8f27dd84-5547-4873-bb80-3e59e5717546",
                            "online": False,
                            "name": "RED-DESKTOP",
                            "domain": "mirumon.dev",
                            "last_user": {
                                "name": "aredruss",
                                "fullname": "Alexander Medyanik",
                                "domain": "mirumon.dev",
                            },
                        },
                    ]
                }
            },
        },
    },
)
async def devices_list() -> List[detail.DeviceOverview]:
    return [
        {
            "id": "dd8475c9-80b8-472a-a7ba-c5aeff36fb9d",
            "online": True,
            "name": "Manjaro-Desktop",
            "domain": "mirumon.dev",
            "last_user": {
                "name": "nick",
                "fullname": "Nick Khitrov",
                "domain": "mirumon.dev",
            },
        },
        {
            "id": "8f27dd84-5547-4873-bb80-3e59e5717546",
            "online": False,
            "name": "RED-DESKTOP",
            "domain": "mirumon.dev",
            "last_user": {
                "name": "aredruss",
                "fullname": "Alexander Medyanik",
                "domain": "mirumon.dev",
            },
        },
    ]


@router.get(
    path=path(EventTypes.detail),
    name=name(EventTypes.detail),
    description=strings.DEVICE_DETAIL_DESCRIPTION,
    dependencies=[Depends(check_user_scopes([UserScopes.read]))],
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
