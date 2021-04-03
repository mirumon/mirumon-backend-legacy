import asyncio
import uuid
from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError

from mirumon.application.devices.commands.sync_device_system_info_command import (
    SyncDeviceSystemInfoCommand,
)
from mirumon.application.devices.devices_repo import DeviceRepository
from mirumon.application.repositories import DeviceBrokerRepo
from mirumon.domain.devices.entities import Device
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.api.devices.http_endpoints.models.detail import DeviceDetail
from mirumon.resources import strings

router = APIRouter()


@router.get(
    path="/devices",
    name="devices:list",
    summary="Get Devices",
    description=strings.DEVICES_LIST_DESCRIPTION,
    response_model=List[DeviceDetail],
)
async def devices_list(
    devices_repo: DeviceRepository = Depends(get_repository(DeviceRepository)),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> List[DeviceDetail]:
    devices = await devices_repo.all()
    sync_id = uuid.uuid4()
    tasks = []
    for device in devices:
        t = asyncio.create_task(_sync_online_device(broker_repo, device, sync_id))
        tasks.append(t)

    online_devices_queue = asyncio.Queue()
    for result in asyncio.as_completed(tasks, timeout=5):
        try:
            device_info = await result
            await online_devices_queue.put(device_info)
        except RuntimeError:
            logger.debug(f"device:{device.id} is offline or rpc timeout")

    online_ids = set()
    online_devices = []
    for _ in range(online_devices_queue.qsize()):
        device_info = online_devices_queue.get_nowait()
        online_ids.add(device_info.id)
        online_devices.append(device_info)

    device_ids = {d.id for d in devices}
    offline_ids = device_ids.difference(online_ids)

    offline_devices = _prepare_offline_devices(devices, offline_ids)
    return online_devices + offline_devices


def _prepare_offline_devices(devices, offline_ids):
    result = []
    for d in devices:
        if d.id in offline_ids:
            try:
                device = DeviceDetail(
                    id=d.id, online=False, **d.properties["system_info"]
                )
                result.append(device)
            except KeyError:
                logger.warning(f"not found system_info property for device:{d.id}")
    return result


async def _sync_online_device(
    broker_repo: DeviceBrokerRepo, device: Device, sync_id: uuid.UUID
):
    command = SyncDeviceSystemInfoCommand(device_id=device.id, sync_id=sync_id)
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.consume(command.sync_id)
        device = DeviceDetail(id=device.id, online=True, **event["event_attributes"])
        return device
    except asyncio.exceptions.TimeoutError:
        raise RuntimeError("Timeout error on fetching device online status")
    except ValidationError as error:
        logger.bind(payload=error.errors()).error(
            f"validation error on event:{command.sync_id} for device:{device.id}"
        )
        raise RuntimeError("Validation error on fetching device online status")
