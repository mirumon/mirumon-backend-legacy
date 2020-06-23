from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies.user_auth import check_user_scopes
from app.domain.device.detail import DeviceDetail
from app.domain.event.types import EventTypes
from app.domain.user.scopes import UserScopes
from app.resources import strings

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/{0}/{1}".format("{device_id}", event)


@router.post(
    path=path(EventTypes.execute),
    summary=EventTypes.execute.capitalize(),
    description=strings.DEVICE_EXECUTE_DESCRIPTION,
    dependencies=[Depends(check_user_scopes([UserScopes.execute]))],
    # response_model=ExecuteResult,
)
async def execute_command_on_device(
    # command_params: ExecuteCommand,
    # client: app.services.devices.client.DeviceClient = Depends(get_client),
    # events_manager: EventsManager = Depends(events_manager_retriever()),
    # sync_id: SyncID = Depends(get_new_sync_id),
) -> DeviceDetail:
    pass
    # event_payload = EventInRequest(
    #     method=EventTypes.shutdown, event_params=command_params, sync_id=sync_id
    # )
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


@router.post(
    path=path(EventTypes.shutdown),
    summary=EventTypes.shutdown.capitalize(),
    description=strings.SHUTDOWN_DESCRIPTION,
    # response_model=shutdown.Shutdown,
)
async def shutdown_device(
    # client: app.services.devices.client.DeviceClient = Depends(get_client),
    # events_manager: EventsManager = Depends(events_manager_retriever()),
    # sync_id: SyncID = Depends(get_new_sync_id),
) -> Any:
    pass
    # event_payload = EventInRequest(method=EventTypes.shutdown, sync_id=sync_id)
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
