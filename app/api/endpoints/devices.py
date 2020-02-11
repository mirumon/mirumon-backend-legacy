from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies.managers import (
    clients_manager_retriever,
    events_manager_retriever,
)
from app.api.dependencies.rest_api import get_client, get_new_sync_id
from app.common import strings
from app.models.domain.types import DeviceEventType, SyncID
from app.models.schemas.devices import detail, execute, hardware, shutdown, software
from app.models.schemas.devices.execute import ExecuteCommand
from app.models.schemas.events.rest import (
    EventInRequest,
    RegistrationInRequest,
    RegistrationInResponse,
)
from app.services import clients
from app.services.authentication import check_device_shared_token, generate_new_device
from app.services.clients_manager import ClientsManager
from app.services.devices import get_devices_list
from app.services.events_manager import EventsManager

router = APIRouter()


# TODO: refactor duplicate code
# TODO: add other events for hardware


def _path(event: str) -> str:
    return "/{0}/{1}".format("{device_uid}", event)


def _name(event: str) -> str:
    return f"events:{event}"


@router.post(
    "/registration",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=RegistrationInResponse,
    name=_name("registration"),
    summary="Registration",
    description=strings.DEVICE_REGISTRATION_DESCRIPTION,
)
async def register_device(
    registration_data: RegistrationInRequest,
) -> RegistrationInResponse:
    if not await check_device_shared_token(registration_data.shared_token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=strings.INVALID_SHARED_TOKEN
        )

    device_token = await generate_new_device()
    return RegistrationInResponse(device_token=device_token)


@router.get(
    path="",
    response_model=List[detail.DeviceOverview],
    name=_name(DeviceEventType.list),
    summary=DeviceEventType.list.capitalize(),
    description=strings.DEVICES_LIST_DESCRIPTION,
)
async def devices_list(
    clients_manager: ClientsManager = Depends(clients_manager_retriever()),
    events_manager: EventsManager = Depends(events_manager_retriever()),
) -> List[detail.DeviceOverview]:
    return await get_devices_list(clients_manager, events_manager)


@router.get(
    path=_path(DeviceEventType.detail),
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
