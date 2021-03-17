import uuid

from fastapi import APIRouter, Depends, Response
from starlette import status

from mirumon.application.devices.commands.execute_on_device_command import (
    ExecuteOnDeviceCommand,
)
from mirumon.application.repositories import DeviceBrokerRepo
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.api.devices.http_endpoints.models.execute import ExecuteCommandParams

router = APIRouter()


@router.post(
    path="/devices/{device_id}/execute",
    name="devices:execute",
    summary="Execute shell command on Device",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
async def execute_command_on_device(
    device_id: DeviceID,
    execute_params: ExecuteCommandParams,
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> None:
    command = ExecuteOnDeviceCommand(
        device_id=device_id, sync_id=uuid.uuid4(), command_attributes=execute_params
    )
    await broker_repo.send_command(command)