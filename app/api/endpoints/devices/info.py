from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies.services import get_users_service
from app.domain.device import detail, execute, hardware, shutdown, software
from app.domain.device.detail import DeviceDetail
from app.domain.device.execute import ExecuteCommand
from app.domain.event.rest import (
    EventInRequest,
)
from app.domain.event.types import DeviceEventType
from app.resources import strings
from app.services.users.users_service import UsersService

router = APIRouter()


def _name(event: str) -> str:
    return "devices:{0}".format(event)


def _path(event: str) -> str:
    return "/{0}/{1}".format("{device_uid}", event)


@router.get(
    path="",
    response_model=List[detail.DeviceOverview],
    name=_name(DeviceEventType.list),
    summary=DeviceEventType.list.capitalize(),
    description=strings.DEVICES_LIST_DESCRIPTION,
)
async def devices_list(
    users_service: UsersService = Depends(get_users_service)
) -> List[detail.DeviceOverview]:
    return await users_service


@router.get(
    path="",
    name=_name(DeviceEventType.detail),
    summary=DeviceEventType.detail.capitalize(),
    description=strings.DEVICE_DETAIL_DESCRIPTION,
    response_model=detail.DeviceDetail,
)
async def get_device_detail(
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
) -> detail.DeviceDetail:
    event_payload = EventInRequest(
        method=DeviceEventType.detail, sync_id=events_manager.register_event(),
    )
    await client.send_event(event_payload)
    try:
        payload = await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
        return DeviceDetail(uid=client.device_uid, online=True, **payload)
    except WebSocketDisconnect:
        error_detail = (
            strings.EVENT_NOT_SUPPORTED
            if client.is_connected
            else strings.DEVICE_DISCONNECTED
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.get(
    path=_path(DeviceEventType.hardware),
    name=_name(DeviceEventType.hardware),
    summary=DeviceEventType.hardware.capitalize(),
    description=strings.DEVICE_HARDWARE_DESCRIPTION,
    response_model=hardware.HardwareModel,
)
async def get_device_hardware(
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> hardware.HardwareModel:
    event_payload = EventInRequest(method=DeviceEventType.hardware, sync_id=sync_id)
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


@router.get(
    path=_path(DeviceEventType.software),
    name=_name(DeviceEventType.software),
    summary=DeviceEventType.software.capitalize(),
    description=strings.DEVICE_SOFTWARE_DESCRIPTION,
    response_model=List[software.InstalledProgram],
)
async def get_device_software(
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> detail.DeviceDetail:
    event_payload = EventInRequest(method=DeviceEventType.software, sync_id=sync_id)
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
    path=_path(DeviceEventType.execute),
    name=_name(DeviceEventType.execute),
    summary=DeviceEventType.execute.capitalize(),
    description=strings.DEVICE_EXECUTE_DESCRIPTION,
    response_model=execute.ExecuteResult,
)
async def execute_command_on_device(
    command_params: ExecuteCommand,
    client: clients.DeviceClient = Depends(get_client),
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
    client: clients.DeviceClient = Depends(get_client),
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
