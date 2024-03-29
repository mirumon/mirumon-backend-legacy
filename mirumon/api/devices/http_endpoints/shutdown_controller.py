import uuid

from fastapi import APIRouter, Depends, Response
from starlette import status

from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.application.devices.commands.shutdown_device_command import (
    ShutdownDeviceCommand,
)
from mirumon.application.devices.device_broker_repo import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device

router = APIRouter()


@router.post(
    path="/devices/{device_id}/shutdown",
    name="devices:shutdown",
    summary="Shutdown Device",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
async def shutdown_device(
    device: Device = Depends(get_registered_device),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> None:
    command = ShutdownDeviceCommand(device_id=device.id, correlation_id=uuid.uuid4())
    await broker_repo.send_command(command)
