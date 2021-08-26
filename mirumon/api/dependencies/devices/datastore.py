from fastapi import Depends, HTTPException

from mirumon.api.dependencies.repositories import get_repository
from mirumon.application.devices.device_repo import DeviceDoesNotExist, DeviceRepository
from mirumon.domain.devices.entities import Device, DeviceID


async def get_registered_device(
    device_id: DeviceID,
    repo: DeviceRepository = Depends(get_repository(DeviceRepository)),
) -> Device:
    try:
        return await repo.get(device_id)
    except DeviceDoesNotExist:
        raise HTTPException(status_code=404, detail="device not found")
