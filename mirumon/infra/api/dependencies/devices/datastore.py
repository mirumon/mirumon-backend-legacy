from fastapi import Depends, HTTPException

from mirumon.application.devices.devices_repo import (
    DeviceDoesNotExist,
    DeviceRepository,
)
from mirumon.domain.devices.entities import Device, DeviceID
from mirumon.infra.api.dependencies.repositories import get_repository


async def get_registered_device(
    device_id: DeviceID,
    repo: DeviceRepository = Depends(get_repository(DeviceRepository)),
) -> Device:
    try:
        return await repo.get(device_id)
    except DeviceDoesNotExist:
        raise HTTPException(status_code=404, detail="device not found")
