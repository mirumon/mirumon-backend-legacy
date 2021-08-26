from typing import List

from fastapi import APIRouter, Depends

from mirumon.application.devices.devices_repo import DeviceRepository
from mirumon.application.devices.devices_socket_repo import DevicesSocketRepo
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.devices.http_endpoints.models.device_in_list_response import (
    DeviceInListResponse,
)
from mirumon.resources import strings

router = APIRouter()


@router.get(
    path="/devices",
    name="devices:list",
    summary="Get Devices",
    description=strings.DEVICES_LIST_DESCRIPTION,
    response_model=List[DeviceInListResponse],
)
async def devices_list(
    devices_repo: DeviceRepository = Depends(get_repository(DeviceRepository)),
    socket_repo: DevicesSocketRepo = Depends(get_repository(DevicesSocketRepo)),
) -> List[DeviceInListResponse]:
    devices = await devices_repo.all()

    results = []
    for device in devices:
        is_online = await socket_repo.is_connected(device.id)
        result = DeviceInListResponse(id=device.id, name=device.name, online=is_online)
        results.append(result)

    return results
