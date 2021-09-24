import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.get_devices_hardware_response import (
    GetDeviceHardwareResponse,
)
from mirumon.application.devices.commands.sync_device_hardware_command import (
    SyncDeviceHardwareCommand,
)
from mirumon.application.devices.device_broker_repo import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device
from mirumon.resources import strings

router = APIRouter()


@router.get(
    path="/devices/{device_id}/hardware",
    name="devices:hardware",
    summary="Get Device Hardware",
    description=strings.DEVICES_HARDWARE_DESCRIPTION,
    response_model=GetDeviceHardwareResponse,
)
async def get_device_hardware(
    device: Device = Depends(get_registered_device),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> GetDeviceHardwareResponse:
    hardware = device.get_hardware()  # type:ignore

    if hardware:
        return GetDeviceHardwareResponse.parse_obj(hardware)

    command = SyncDeviceHardwareCommand(
        device_id=device.id, correlation_id=uuid.uuid4()
    )
    await broker_repo.send_command(command)
    try:
        event = await broker_repo.get(device.id, command.correlation_id)  # type: ignore
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    return GetDeviceHardwareResponse(**event["event_attributes"])
