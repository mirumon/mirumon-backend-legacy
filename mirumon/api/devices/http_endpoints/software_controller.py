import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.get_list_device_software_response import (  # noqa: E501
    GetListDeviceSoftware,
)
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
    response_model=GetListDeviceSoftware,
)
async def get_device_software(
    device: Device = Depends(get_registered_device),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> GetListDeviceSoftware:
    software = device.get_software()  # type: ignore

    if software:
        return GetListDeviceSoftware.parse_obj(software)

    command = SyncDeviceSoftwareCommand(
        device_id=device.id, correlation_id=uuid.uuid4()
    )
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.get(device.id, command.correlation_id)  # type: ignore
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    else:
        return GetListDeviceSoftware(
            __root__=event["event_attributes"]["installed_programs"]
        )
