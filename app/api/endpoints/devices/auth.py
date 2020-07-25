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
    status_code=status.HTTP_201_CREATED,
    name="devices:registration",
    summary="Register device",
    description=strings.DEVICE_REGISTRATION_DESCRIPTION,
    response_model=DeviceAuthInResponse,
)
async def register_device(
    credentials: DeviceAuthInRequest,
    devices_service: DevicesService = Depends(get_devices_service),
) -> DeviceAuthInResponse:
    is_shared_token_valid = devices_service.check_device_credentials(credentials)
    if not is_shared_token_valid:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=strings.INVALID_SHARED_KEY,
        )

    token = await devices_service.register_new_device()
    return {"token": token}
