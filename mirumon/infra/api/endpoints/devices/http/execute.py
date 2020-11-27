from fastapi import APIRouter, Depends, HTTPException, Response
from loguru import logger
from starlette import status

from mirumon.application.devices.events_service import EventsService
from mirumon.domain.devices.entities import DeviceID
from mirumon.infra.api.dependencies.services import get_service
from mirumon.infra.api.endpoints.devices.http.models.execute import ExecuteCommandParams
from mirumon.infra.events.events import EventParams, EventTypes

DEVICE_UNAVAILABLE_ERROR = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="device unavailable"
)

router = APIRouter()


@router.post(
    path="/{device_id}/execute",
    name="devices:execute",
    summary="Execute Command on Device",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
async def execute_command_on_device(
    device_id: DeviceID,
    execute_params: ExecuteCommandParams,
    events_service: EventsService = Depends(get_service(EventsService)),
) -> None:
    params = EventParams(execute_params.dict())
    try:
        event_id = await events_service.send_event_request(
            event_type=EventTypes.execute, device_id=device_id, params=params
        )
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        )

    try:
        await events_service.listen_event(event_id, EventTypes.execute)
    except RuntimeError:
        logger.debug(f"listening timeout for event:{event_id}")
        raise DEVICE_UNAVAILABLE_ERROR
