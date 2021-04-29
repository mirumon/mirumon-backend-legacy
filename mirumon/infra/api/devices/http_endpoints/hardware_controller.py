import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.application.devices.commands.sync_device_hardware_command import (
    SyncDeviceHardwareCommand,
)
from mirumon.application.devices.devices_broker_repo import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device
from mirumon.infra.api.dependencies.devices.datastore import get_registered_device
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.api.devices.http_endpoints.models.hardware import HardwareModel
from mirumon.resources import strings

router = APIRouter()


@router.get(
    path="/devices/{device_id}/hardware",
    name="devices:hardware",
    summary="Get Device Hardware",
    description=strings.DEVICES_HARDWARE_DESCRIPTION,
    response_model=HardwareModel,
)
async def get_device_hardware(
    device: Device = Depends(get_registered_device),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> HardwareModel:
    command = SyncDeviceHardwareCommand(device_id=device.id, sync_id=uuid.uuid4())
    await broker_repo.send_command(command)
    try:
        event = await broker_repo.consume(device.id, command.sync_id)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    return HardwareModel(**event["event_attributes"])
