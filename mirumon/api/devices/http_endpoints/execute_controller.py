import uuid

from fastapi import APIRouter, Depends, Response
from starlette import status

from mirumon.application.devices.commands.execute_on_device_command import (
    ExecuteOnDeviceCommand,
)
from mirumon.application.devices.devices_broker_repo import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device
from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.execute import ExecuteCommandParams

router = APIRouter()


@router.post(
    path="/devices/{device_id}/execute",
    name="devices:execute",
    summary="Execute shell command on Device",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
async def execute_command_on_device(
    execute_params: ExecuteCommandParams,
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
    device: Device = Depends(get_registered_device),
) -> None:
    command = ExecuteOnDeviceCommand(
        device_id=device.id,
        sync_id=uuid.uuid4(),
        command_attributes=execute_params.dict(),
    )
    await broker_repo.send_command(command)
