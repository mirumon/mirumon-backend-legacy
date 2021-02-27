import uuid

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from mirumon.application.devices.commands.sync_commands import (
    SyncDeviceSystemInfoCommand,
)
from mirumon.application.events.models import EventTypes
from mirumon.application.repositories import BrokerRepo
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.api.devices.http_endpoints.models.detail import DeviceDetail
from mirumon.resources import strings

router = APIRouter()


def name(event: str) -> str:
    return "devices:{0}".format(event)


def path(event: str) -> str:
    return "/devices/{0}/{1}".format("{device_id}", event)


@router.get(
    path=path(EventTypes.detail),
    name=name(EventTypes.detail),
    summary="Get Device",
    description=strings.DEVICES_DETAIL_DESCRIPTION,
    response_model=DeviceDetail,
)
async def get_device_detail(
    device_id: DeviceID,
    broker_repo: BrokerRepo = Depends(get_repository(BrokerRepo)),
) -> DeviceDetail:
    command = SyncDeviceSystemInfoCommand(device_ids=[device_id], sync_id=uuid.uuid4())
    await broker_repo.publish_command(command)

    event = await broker_repo.consume(command.sync_id)
    print(event)
    return DeviceDetail(id=device_id, online=True, **event["event_attributes"])
