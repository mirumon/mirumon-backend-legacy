import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.get_device_system_response import (
    GetDeviceSystemResponse,
)
from mirumon.application.devices.commands.sync_device_system_command import (
    SyncDeviceSystemCommand,
)
from mirumon.application.devices.device_broker_repo import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device

router = APIRouter()


@router.get(
    path="/devices/{device_id}/system",
    name="devices:system",
    summary="Get Device System",
    response_model=GetDeviceSystemResponse,
)
async def get_device_system(
    device: Device = Depends(get_registered_device),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> GetDeviceSystemResponse:
    system = device.get_system()  # type: ignore

    if system:
        return GetDeviceSystemResponse(system_attributes=system)

    command = SyncDeviceSystemCommand(device_id=device.id, correlation_id=uuid.uuid4())
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.get(device.id, command.correlation_id)  # type: ignore
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    return GetDeviceSystemResponse(system_attributes=event["event_attributes"])
