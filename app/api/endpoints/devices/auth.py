from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.dependencies.services import get_devices_service
from app.domain.device.auth import DeviceAuthInRequest, DeviceAuthInResponse
from app.resources import strings
from app.services.devices.devices_service import DevicesService

router = APIRouter()


@router.post(
    "/registration",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=DeviceAuthInResponse,
    name="devices:registration",
    summary="Device Registration",
    description=strings.DEVICE_REGISTRATION_DESCRIPTION,
)
async def register_device(
    credentials: DeviceAuthInRequest,
    devices_service: DevicesService = Depends(get_devices_service),
) -> DeviceAuthInRequest:
    is_shared_token_valid = await devices_service.check_device_credentials(credentials)
    if not is_shared_token_valid:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=strings.INVALID_SHARED_TOKEN
        )

    return await devices_service.register_new_device()
