from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from mirumon.api.dependencies.services import get_service
from mirumon.api.dependencies.users.permissions import check_user_scopes
from mirumon.api.devices.http_endpoints.models.create_device_by_shared_key_request import (
    CreateDeviceBySharedKeyRequest,
)
from mirumon.api.devices.http_endpoints.models.create_device_by_shared_key_response import (
    CreateDeviceBySharedKeyResponse,
)
from mirumon.api.devices.http_endpoints.models.create_device_request import (
    CreateDeviceRequest,
)
from mirumon.api.devices.http_endpoints.models.create_device_response import (
    CreateDeviceResponse,
)
from mirumon.application.devices.auth_service import DevicesAuthService
from mirumon.application.devices.device_service import DevicesService
from mirumon.domain.users.scopes import DevicesScopes
from mirumon.resources import strings

router = APIRouter()


@router.post(
    "/devices",
    status_code=status.HTTP_201_CREATED,
    name="devices:create",
    summary="Create device",
    description=strings.DEVICES_CREATE_DESCRIPTION,
    response_model=CreateDeviceResponse,
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)
async def create_device(
    device_params: CreateDeviceRequest,
    auth_service: DevicesAuthService = Depends(get_service(DevicesAuthService)),
    devices_service: DevicesService = Depends(get_service(DevicesService)),
) -> CreateDeviceResponse:
    device = await devices_service.register_new_device(name=device_params.name)
    token = auth_service.create_device_token(device)
    return CreateDeviceResponse(token=token, name=device.name)


@router.post(
    "/devices/by/shared",
    status_code=status.HTTP_201_CREATED,
    name="devices:create-by-shared",
    summary="Create device by Shared Key",
    response_model=CreateDeviceBySharedKeyResponse,
)
async def create_device_by_shared_key(
    credentials: CreateDeviceBySharedKeyRequest,
    auth_service: DevicesAuthService = Depends(get_service(DevicesAuthService)),
    devices_service: DevicesService = Depends(get_service(DevicesService)),
) -> CreateDeviceBySharedKeyResponse:
    is_shared_token_valid = auth_service.is_valid_shared_key(credentials.shared_key)
    if not is_shared_token_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.INVALID_SHARED_KEY,
        )

    device = await devices_service.register_new_device(name=credentials.name)
    token = auth_service.create_device_token(device)
    return CreateDeviceBySharedKeyResponse(token=token, name=device.name)
