import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.application.devices.commands.sync_device_hardware_command import (
    SyncDeviceHardwareCommand,
)
from mirumon.application.devices.commands.sync_device_software_command import (
    SyncDeviceSoftwareCommand,
)
from mirumon.application.repositories import DeviceBrokerRepo
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.api.devices.http_endpoints.models.hardware import HardwareModel
from mirumon.infra.api.devices.http_endpoints.models.software import (
    ListInstalledProgram,
)
from mirumon.resources import strings

router = APIRouter()


@router.get(
    path="/devices/{device_id}/software",
    name="devices:software",
    summary="Get Device Software",
    description=strings.DEVICES_SOFTWARE_DESCRIPTION,
    response_model=ListInstalledProgram,
)
async def get_device_software(
    device_id: DeviceID,
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> ListInstalledProgram:
    command = SyncDeviceSoftwareCommand(device_id=device_id, sync_id=uuid.uuid4())
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.consume(command.sync_id)
        return ListInstalledProgram(
            __root__=event["event_attributes"]["installed_programs"]
        )
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )


@router.get(
    path="/devices/{device_id}/hardware",
    name="devices:hardware",
    summary="Get Device Hardware",
    description=strings.DEVICES_HARDWARE_DESCRIPTION,
    response_model=HardwareModel,
)
async def get_device_hardware(
    device_id: DeviceID,
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> HardwareModel:
    command = SyncDeviceHardwareCommand(device_id=device_id, sync_id=uuid.uuid4())
    await broker_repo.send_command(command)
    try:
        event = await broker_repo.consume(command.sync_id)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    return HardwareModel(**event["event_attributes"])
