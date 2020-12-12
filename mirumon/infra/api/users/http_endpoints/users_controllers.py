from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from mirumon.application.users.auth_service import AuthUsersService
from mirumon.infra.api.dependencies.services import get_service
from mirumon.infra.api.users.http_endpoints.models.crud import (
    UserInCreateRequest,
    UserInCreateResponse,
)
from mirumon.resources import strings

router = APIRouter()


@router.post(
    "/users",
    name="users:create",
    summary="Create User",
    status_code=HTTP_201_CREATED,
    response_model=UserInCreateResponse,
)
async def create_user(
    new_user: UserInCreateRequest,
    auth_users_service: AuthUsersService = Depends(get_service(AuthUsersService)),
) -> UserInCreateResponse:
    try:
        user = await auth_users_service.register_new_user(
            new_user.username, new_user.password, new_user.scopes
        )
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=strings.USERNAME_TAKEN,
        )

    return UserInCreateResponse.parse_obj(user.dict())
