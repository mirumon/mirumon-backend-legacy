from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.websockets import WebSocketDisconnect

import app.services.devices.client
from app.domain.device import detail, execute, shutdown
from app.domain.device.execute import ExecuteCommand
from app.domain.event.rest import EventInRequest
from app.domain.event.types import DeviceEventType
from app.resources import strings

router = APIRouter()


@router.post(
    path=_path(DeviceEventType.execute),
    name=_name(DeviceEventType.execute),
    summary=DeviceEventType.execute.capitalize(),
    description=strings.DEVICE_EXECUTE_DESCRIPTION,
    response_model=execute.ExecuteResult,
)
async def execute_command_on_device(
    command_params: ExecuteCommand,
    client: app.services.devices.client.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> detail.DeviceDetail:
    event_payload = EventInRequest(
        method=DeviceEventType.shutdown, event_params=command_params, sync_id=sync_id
    )
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            strings.EVENT_NOT_SUPPORTED
            if client.is_connected
            else strings.DEVICE_DISCONNECTED
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.post(
    path=_path(DeviceEventType.shutdown),
    name=_name(DeviceEventType.shutdown),
    summary=DeviceEventType.shutdown.capitalize(),
    description=strings.SHUTDOWN_DESCRIPTION,
    response_model=shutdown.Shutdown,
)
async def shutdown_device(
    client: app.services.devices.client.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> detail.DeviceDetail:
    event_payload = EventInRequest(method=DeviceEventType.shutdown, sync_id=sync_id)
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            strings.EVENT_NOT_SUPPORTED
            if client.is_connected
            else strings.DEVICE_DISCONNECTED
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )
