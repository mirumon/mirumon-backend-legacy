from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.websockets import WebSocketDisconnect

from app.api.dependencies.managers import EventsManager, events_manager_retriever
from app.api.dependencies.rest_api import get_client, get_new_sync_id
from app.models.schemas.computers import details, execute, hardware, shutdown, software
from app.models.schemas.computers.execute import ExecuteCommand
from app.models.schemas.events.rest import EventInRequest
from app.models.schemas.events.types import EventType, SyncID
from app.services import clients

# TODO: refactor duplicate code
# TODO: add other events for hardware


router = APIRouter()


@router.get(
    "/{0}/{1}".format("{device_uid}", EventType.details),
    name=f"events:{EventType.details}",
    summary=f"Device {EventType.details.capitalize()}",
    response_model=details.ComputerDetails,
)
async def get_device_detail(
    client: clients.Client = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
) -> details.ComputerDetails:
    event_payload = EventInRequest(
        method=EventType.details, sync_id=events_manager.register_event(),
    )
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            f"{EventType.details} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.get(
    "/{0}/{1}".format("{device_uid}", EventType.hardware),
    name=f"events:{EventType.hardware}",
    summary=f"Device {EventType.hardware.capitalize()}",
    response_model=hardware.HardwareModel,
)
async def get_device_hardware(
    client: clients.Client = Depends(get_client),
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
            f"{EventType.details} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.get(
    "/{0}/{1}".format("{device_uid}", EventType.installed_programs),
    name=f"events:{EventType.installed_programs}",
    summary=f"Device {EventType.installed_programs.capitalize()}",
    response_model=List[software.InstalledProgram],
)
async def get_device_software(
    client: clients.Client = Depends(get_client),
    events_manager: EventsManager = Depends(events_manager_retriever()),
    sync_id: SyncID = Depends(get_new_sync_id),
) -> details.ComputerDetails:
    event_payload = EventInRequest(method=EventType.installed_programs, sync_id=sync_id)
    await client.send_event(event_payload)
    try:
        return await events_manager.wait_event_from_client(
            sync_id=event_payload.sync_id, client=client
        )
    except WebSocketDisconnect:
        error_detail = (
            f"{EventType.details} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.post(
    "/{0}/{1}".format("{device_uid}", EventType.shutdown),
    name=f"events:{EventType.shutdown}",
    summary=f"Device {EventType.shutdown.capitalize()}",
    response_model=shutdown.Shutdown,
)
async def shutdown_device(
    client: clients.Client = Depends(get_client),
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
            f"{EventType.details} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )


@router.post(
    "/{0}/{1}".format("{device_uid}", EventType.execute),
    name=f"events:{EventType.execute}",
    summary=f"Device {EventType.execute.capitalize()}",
    response_model=execute.ExecuteResult,
)
async def execute_command_on_device(
    command_params: ExecuteCommand,
    client: clients.Client = Depends(get_client),
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
            f"{EventType.details} event is not supported by device"
            if client.is_connected
            else "device disconnected"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error_detail,
        )
