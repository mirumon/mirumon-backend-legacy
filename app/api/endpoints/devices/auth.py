from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.dependencies.services import get_devices_auth_service, get_devices_service
from app.api.models.http.device_auth import DeviceAuthInRequest, DeviceAuthInResponse
from app.resources import strings
from app.services.devices.auth_service import DevicesAuthService
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
    auth_service: DevicesAuthService = Depends(get_devices_auth_service),
    devices_service: DevicesService = Depends(get_devices_service),
) -> DeviceAuthInResponse:
    is_shared_token_valid = auth_service.is_valid_shared_key(credentials.shared_key)
    if not is_shared_token_valid:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=strings.INVALID_SHARED_KEY,
        )

    device = await devices_service.register_new_device()
    token = auth_service.create_device_token(device)
    return DeviceAuthInResponse(token=token)
