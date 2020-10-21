from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST

from app.api.dependencies.services import get_service
from app.api.dependencies.users.permissions import check_user_scopes
from app.api.models.http.devices.auth import DeviceAuthInRequest, DeviceAuthInResponse
from app.domain.user.scopes import DevicesScopes
from app.resources import strings
from app.services.devices.auth_service import DevicesAuthService
from app.services.devices.devices_service import DevicesService

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    name="devices:create",
    summary="Create device",
    description=strings.DEVICES_CREATE_DESCRIPTION,
    response_model=DeviceAuthInResponse,
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)
async def create_device(
    auth_service: DevicesAuthService = Depends(get_service(DevicesAuthService)),
    devices_service: DevicesService = Depends(get_service(DevicesService)),
) -> DeviceAuthInResponse:
    device = await devices_service.register_new_device()
    token = auth_service.create_device_token(device)
    return DeviceAuthInResponse(token=token)


@router.post(
    "/by/shared",
    status_code=status.HTTP_201_CREATED,
    name="devices:create-by-shared",
    summary="Create device by Shared Key",
    response_model=DeviceAuthInResponse,
)
async def create_device_by_shared_key(
    credentials: DeviceAuthInRequest,
    auth_service: DevicesAuthService = Depends(get_service(DevicesAuthService)),
    devices_service: DevicesService = Depends(get_service(DevicesService)),
) -> DeviceAuthInResponse:
    is_shared_token_valid = auth_service.is_valid_shared_key(credentials.shared_key)
    if not is_shared_token_valid:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=strings.INVALID_SHARED_KEY,
        )

    device = await devices_service.register_new_device()
    token = auth_service.create_device_token(device)
    return DeviceAuthInResponse(token=token)
