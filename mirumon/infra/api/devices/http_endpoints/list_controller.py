import asyncio
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError

from mirumon.application.devices.commands.sync_device_system_info_command import (
    SyncDeviceSystemInfoCommand,
)
from mirumon.application.devices.devices_repo import DeviceRepository
from mirumon.application.devices.devices_broker_repo import DeviceBrokerRepo
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
    # get all devices from db
    devices = await devices_repo.all()

    # results = await asyncio.gather(*[_get_device_system_info(broker_repo, d) for d in devices])

    events_to_device = {}
    for device in devices:
        sync_id = uuid.uuid4()
        command = SyncDeviceSystemInfoCommand(device_id=device.id, sync_id=sync_id)
        await broker_repo.send_command(command)
        events_to_device[command.sync_id] = device

    results = []
    try:
        async for event in broker_repo.bulk_consume():
            logger.debug("got event from bulk_consume: {}", event)
            try:
                sync_id = event.get("sync_id")
                device = events_to_device[sync_id]
                result = DeviceDetail(id=device.id, online=True, **event.get("event_attributes"))
                logger.debug(f"append online result: {result}")
                results.append(result)
            except KeyError as e:
                logger.debug(f"not found registered command for sync_id:{e}")
                continue
            except Exception as error:
                logger.error(f"got error on system_info sync in list api: {error}")
                device_system_info = device.properties.get("system_info")
                if not device_system_info:
                    logger.warning(
                        f"not found system_info data in database for device:{device.id}")
                    continue
                result = DeviceDetail(id=device.id, online=False, **device_system_info)
                results.append(result)
    except asyncio.exceptions.TimeoutError:
        logger.debug("bulk timeout in devices list")
    return results
    #
    # old code
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
    for task in asyncio.as_completed(tasks):
        try:
            device_info = await task
            await online_devices_queue.put(device_info)
        except RuntimeError as e:
            logger.debug(f"device online sync error:{e}")

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

    return online_devices + offline_devices


async def _sync_online_device(broker_repo: DeviceBrokerRepo, device: Device) -> DeviceDetail:
    sync_id = uuid.uuid4()
    command = SyncDeviceSystemInfoCommand(device_id=device.id, sync_id=sync_id)
    await broker_repo.send_command(command)

    try:
        event = await broker_repo.consume(device.id, command.sync_id)
        return DeviceDetail(id=device.id, online=True, **event["event_attributes"])
    except asyncio.exceptions.TimeoutError:
        raise RuntimeError(f"Timeout error on fetching device:{device.id} online status")
    except ValidationError as error:
        logger.bind(payload=error.errors()).error(
            f"validation error on event:{command.sync_id} for device:{device.id}"
        )
        raise RuntimeError(f"Validation error on fetching device:{device.id} online status")

# 2
async def _get_device_system_info(broker_repo, device: Device) -> Optional[DeviceDetail]:
    sync_id = uuid.uuid4()
    command = SyncDeviceSystemInfoCommand(device_id=device.id, sync_id=sync_id)
    await broker_repo.send_command(command)
    try:
        event = await broker_repo.consume(device.id, command.sync_id)
        return DeviceDetail(id=device.id, online=True, **event["event_attributes"])
    except Exception as error:
        logger.error(f"got error on system_info sync in list api: {error}")
        device_system_info = device.properties.get("system_info")
        if not device_system_info:
            logger.warning(f"not found system_info data in database for device:{device.id}")
            return None

        return DeviceDetail(id=device.id, online=False, **device_system_info)

