import uuid

from fastapi import APIRouter, Depends, Response
from starlette import status

from mirumon.application.devices.commands.shutdown_device_command import (
    ShutdownDeviceCommand,
)
from mirumon.application.repositories import DeviceBrokerRepo
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.repositories import get_repository

router = APIRouter()


@router.post(
    path="/devices/{device_id}/shutdown",
    name="devices:shutdown",
    summary="Shutdown Device",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
async def shutdown_device(
    device_id: DeviceID,
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> None:
    command = ShutdownDeviceCommand(device_id=device_id, sync_id=uuid.uuid4())
    # await broker_repo.send_command(command)
