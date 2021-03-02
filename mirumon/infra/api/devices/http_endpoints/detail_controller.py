import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.application.devices.commands.sync_device_system_info_command import (
    SyncDeviceSystemInfoCommand,
)
from mirumon.application.repositories import DeviceBrokerRepo
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.api.devices.http_endpoints.models.detail import DeviceDetail
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
    device_id: DeviceID,
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> DeviceDetail:
    command = SyncDeviceSystemInfoCommand(device_id=device_id, sync_id=uuid.uuid4())
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.consume(command.sync_id)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    return DeviceDetail(id=device_id, online=True, **event["event_attributes"])
