import uuid
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
from app.models.domain.types import EventType, SyncID
from app.models.schemas.devices import details, execute, hardware, shutdown, software
from app.models.schemas.devices.execute import ExecuteCommand
from app.models.schemas.events.rest import (
    EventInRequest,
    RegistrationInRequest,
    RegistrationInResponse,
)
from app.services import clients
from app.services.authentication import check_device_shared_token
from app.services.clients_manager import ClientsManager
from app.services.devices import get_devices_list
from app.services.events_manager import EventsManager

router = APIRouter()


# TODO: refactor duplicate code
# TODO: add other events for hardware


@router.post(
    "/registration",
    response_model=RegistrationInResponse,
    name="events:registration",
    summary="Registration",
    description="Register a device to receive a token for usage in ws connection",
)
async def register_device(
    registration_data: RegistrationInRequest,
) -> RegistrationInResponse:
    if not await check_device_shared_token(registration_data.shared_token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=strings.INVALID_SHARED_TOKEN
        )
    # TODO: token generation, saving into db
    return RegistrationInResponse(device_token=str(uuid.uuid4()))


@router.get(
    "",
    response_model=List[details.ComputerOverview],
    name="events:list",
    summary="List",
    description="List of all available devices",
)
async def devices_list(
    clients_manager: ClientsManager = Depends(clients_manager_retriever()),
    events_manager: EventsManager = Depends(events_manager_retriever()),
) -> List[details.ComputerOverview]:
    return await get_devices_list(clients_manager, events_manager)


@router.get(
    "/{0}/{1}".format("{device_uid}", EventType.detail),
    name=f"events:{EventType.detail}",
    summary=EventType.detail.capitalize(),
    description="Detail information about device",
    response_model=details.ComputerDetails,
)
async def get_device_detail(
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
) -> details.ComputerDetails:
    event_payload = EventInRequest(
        method=EventType.detail, sync_id=events_manager.register_event(),
    )
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            f"{EventType.detail} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.get(
    "/{0}/{1}".format("{device_uid}", EventType.hardware),
    name=f"events:{EventType.hardware}",
    summary=EventType.hardware.capitalize(),
    description="Hardware information of device",
    response_model=hardware.HardwareModel,
)
async def get_device_hardware(
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> hardware.HardwareModel:
    event_payload = EventInRequest(method=EventType.hardware, sync_id=sync_id)
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            f"{EventType.detail} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.get(
    "/{0}/{1}".format("{device_uid}", EventType.software),
    name=f"events:{EventType.software}",
    summary=EventType.software.capitalize(),
    description="Installed programs on device",
    response_model=List[software.InstalledProgram],
)
async def get_device_software(
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> details.ComputerDetails:
    event_payload = EventInRequest(method=EventType.software, sync_id=sync_id)
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            f"{EventType.detail} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.post(
    "/{0}/{1}".format("{device_uid}", EventType.shutdown),
    name=f"events:{EventType.shutdown}",
    summary=f"{EventType.shutdown.capitalize()}",
    description=(
        "Shutdown device. "
        "Does not disconnect the device from the server "
        "until the device itself turns off"
    ),
    response_model=shutdown.Shutdown,
)
async def shutdown_device(
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> details.ComputerDetails:
    event_payload = EventInRequest(method=EventType.shutdown, sync_id=sync_id)
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            f"{EventType.detail} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.post(
    "/{0}/{1}".format("{device_uid}", EventType.execute),
    name=f"events:{EventType.execute}",
    summary=f"{EventType.execute.capitalize()}",
    description="Background runs a command on the device",
    response_model=execute.ExecuteResult,
)
async def execute_command_on_device(
    command_params: ExecuteCommand,
    client: clients.DeviceClient = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> details.ComputerDetails:
    event_payload = EventInRequest(
        method=EventType.shutdown, event_params=command_params, sync_id=sync_id
    )
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            "event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )
