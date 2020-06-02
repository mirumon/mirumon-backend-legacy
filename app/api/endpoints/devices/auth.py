from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.websockets import WebSocketDisconnect

from app.domain.device import detail, execute, hardware, shutdown, software
from app.domain.device.detail import DeviceDetail
from app.domain.device.execute import ExecuteCommand
from app.domain.event.rest import (
    EventInRequest,
    RegistrationInRequest,
    RegistrationInResponse,
)
from app.resources import strings

router = APIRouter()


# TODO: refactor duplicate code
# TODO: add other events for hardware


@router.post(
    "/registration",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=RegistrationInResponse,
    name="devices:registration",
    summary="Device Registration",
    description=strings.DEVICE_REGISTRATION_DESCRIPTION,
)
async def register_device(
    registration_data: RegistrationInRequest,
) -> RegistrationInResponse:
    if not await check_device_shared_token(registration_data.shared_token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=strings.INVALID_SHARED_TOKEN
        )

    device_token = await generate_new_device()
    return RegistrationInResponse(device_token=device_token)
