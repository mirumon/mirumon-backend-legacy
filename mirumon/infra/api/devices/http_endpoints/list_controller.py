from typing import List

from fastapi import APIRouter, Depends

from mirumon.application.repositories import DeviceBrokerRepo
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
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
) -> List[DeviceDetail]:
    events = []
    # TODO: new method for broadcast sending; gather tasks
    # for device_id in gateway.client_ids:
    #     command = SyncDeviceSystemInfoCommand(device_id=device_id, sync_id=uuid.uuid4())
    #     await broker_repo.send_command(command)

    # try:
    #     event = await broker_repo.consume(command.sync_id)
    # except asyncio.exceptions.TimeoutError:
    #     raise HTTPException(
    #         status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="device unavailable"
    #     )
    #     try:
    #         events.append(
    #             DeviceDetail(id=device_id, online=True, **event["event_attributes"])
    #         )
    #     except ValidationError as error:
    #         logger.bind(payload=error.errors()).warning(
    #             f"validation error on event:{event_id} for device:{device_id}"
    #         )
    return events
