from fastapi import APIRouter, Depends

from mirumon.api.dependencies.devices.datastore import get_registered_device
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.get_device_response import (
    GetDeviceResponse,
)
from mirumon.api.devices.http_endpoints.models.list_devices_response import (
    ListDevicesResponse,
)
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
        result = {"id": device.id, "name": device.name, "online": is_online}
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
) -> GetDeviceResponse:
    is_online = await socket_repo.is_connected(device.id)

    return GetDeviceResponse(id=device.id, name=device.name, online=is_online)
