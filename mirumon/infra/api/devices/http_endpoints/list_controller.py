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
    # response_model=List[DeviceDetail],
)
async def devices_list(
    devices_repo: DeviceRepository = Depends(get_repository(DeviceRepository)),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> List[DeviceDetail]:
    # get all devices from db
    devices = await devices_repo.all()
    device_ids = {d.id for d in devices}

    print(f"device_ids from repo: {device_ids}")
    print()
    # run async command of sync type for each device to check is it online
    tasks = []
    for device in devices:
        t = asyncio.create_task(_sync_online_device(broker_repo, device))
        tasks.append(t)

    # wait for tasks to complete
    # or timeout
    online_devices_queue = asyncio.Queue()
    for task in asyncio.as_completed(tasks, timeout=10):
        try:
            device_info = await task
            await online_devices_queue.put(device_info)
        except RuntimeError:
            logger.debug(f"device:{device.id} is offline or rpc timeout")

    # collect ids of online devices
    # and collect events to return in response
    online_ids = set()
    online_devices = []
    for _ in range(online_devices_queue.qsize()):
        device_info = online_devices_queue.get_nowait()
        print(f"online device info: {device_info}")
        online_ids.add(device_info.id)
        online_devices.append(device_info)

    # collect ids of offline devices
    # to find get them from collection
    offline_ids = device_ids.difference(online_ids)

    print(f"devices: {device_ids}")
    print(f"online: {online_ids}")
    print(f"offline: {offline_ids}")

    offline_devices = []
    for d in devices:
        if d.id in offline_ids:
            try:
                print(f"offline device matched: {d}")
                device = DeviceDetail(
                    id=d.id, online=False, **d.properties["system_info"]
                )
                offline_devices.append(device)
            except KeyError:
                logger.warning(f"not found system_info property for device:{d.id}")

    # r = online_devices + offline_devices
    # return [d.id for d in r]
    return online_devices + offline_devices


async def _sync_online_device(broker_repo: DeviceBrokerRepo, device: Device):
    sync_id = uuid.uuid4()
    command = SyncDeviceSystemInfoCommand(device_id=device.id, sync_id=sync_id)
    print(f"_sync_online_device command: {command}")
    await broker_repo.send_command(command)

    try:
        # bug here
        # sync_id is one fro all devices
        event = await broker_repo.consume(device.id, command.sync_id)
        print(f"_sync_online_device event: {event}")
        if event.get("device_id") != device.id:
            m = f"device id {device.id} not equal with {event.get('device_id')} from event"
            logger.critical(m)
            raise RuntimeError(m)
        return DeviceDetail(id=device.id, online=True, **event["event_attributes"])
    except asyncio.exceptions.TimeoutError:
        raise RuntimeError("Timeout error on fetching device online status")
    except ValidationError as error:
        logger.bind(payload=error.errors()).error(
            f"validation error on event:{command.sync_id} for device:{device.id}"
        )
        raise RuntimeError("Validation error on fetching device online status")
