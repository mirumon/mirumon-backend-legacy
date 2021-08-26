import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.application.devices.commands.sync_device_system_info_command import (
    SyncDeviceSystemInfoCommand,
)
from mirumon.application.devices.devices_broker_repo import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device
from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.detail import DeviceDetail
from mirumon.resources import strings

router = APIRouter()


@router.get(
    path="/devices/{device_id}/detail",
    name="devices:detail",
    summary="Get Device",
    description=strings.DEVICES_DETAIL_DESCRIPTION,
    response_model=DeviceDetail,
)
async def get_device_detail(
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
    device: Device = Depends(get_registered_device),
) -> DeviceDetail:
    command = SyncDeviceSystemInfoCommand(device_id=device.id, sync_id=uuid.uuid4())
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.consume(device.id, command.sync_id)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    return DeviceDetail(id=device.id, online=True, **event["event_attributes"])
