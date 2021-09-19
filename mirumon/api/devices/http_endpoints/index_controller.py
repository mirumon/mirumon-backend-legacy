import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.get_device_response import (
    GetDeviceResponse,
)
from mirumon.api.devices.http_endpoints.models.list_devices_response import (
    ListDevicesResponse,
)
from mirumon.application.devices.commands.sync_device_system_info_command import (
    SyncDeviceSystemInfoCommand,
)
from mirumon.application.devices.device_broker_repo import DeviceBrokerRepo
from mirumon.application.devices.device_repo import DeviceRepository
from mirumon.application.devices.device_socket_repo import DevicesSocketRepo
from mirumon.domain.devices.entities import Device
from mirumon.resources import strings

router = APIRouter()


@router.get(
    path="/devices",
    name="devices:list",
    summary="List Devices",
    description=strings.DEVICES_LIST_DESCRIPTION,
    response_model=ListDevicesResponse,
)
async def list_devices(
    devices_repo: DeviceRepository = Depends(get_repository(DeviceRepository)),
    socket_repo: DevicesSocketRepo = Depends(get_repository(DevicesSocketRepo)),
) -> ListDevicesResponse:
    devices = await devices_repo.all()

    results = []
    for device in devices:
        is_online = await socket_repo.is_connected(device.id)
        result = dict(id=device.id, name=device.name, online=is_online)
        results.append(result)

    return ListDevicesResponse.parse_obj(results)


@router.get(
    path="/devices/{device_id}",
    name="devices:get",
    summary="Get Device",
    description=strings.DEVICES_DETAIL_DESCRIPTION,
    response_model=GetDeviceResponse,
)
async def get_device(
    device: Device = Depends(get_registered_device),
    socket_repo: DevicesSocketRepo = Depends(get_repository(DevicesSocketRepo)),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> GetDeviceResponse:
    system = device.get_system()
    is_online = await socket_repo.is_connected(device.id)

    if system:
        return GetDeviceResponse(id=device.id, online=is_online)

    command = SyncDeviceSystemInfoCommand(device_id=device.id, sync_id=uuid.uuid4())
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.consume(device.id, command.sync_id)
    except asyncio.exceptions.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
        )
    return GetDeviceResponse(id=device.id, online=True, **event["event_attributes"])
