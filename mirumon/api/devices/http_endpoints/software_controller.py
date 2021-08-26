import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.software import ListInstalledProgram
from mirumon.application.devices.commands.sync_device_software_command import (
    SyncDeviceSoftwareCommand,
)
from mirumon.application.devices.device_broker_repo import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device
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
    device: Device = Depends(get_registered_device),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> ListInstalledProgram:
    software = device.get_software()

    if software:
        return ListInstalledProgram.parse_obj(software)

    command = SyncDeviceSoftwareCommand(device_id=device.id, sync_id=uuid.uuid4())
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.consume(device.id, command.sync_id)
        return ListInstalledProgram(
            __root__=event["event_attributes"]["installed_programs"]
        )
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
