from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from mirumon.application.users.auth_service import AuthUsersService
from mirumon.infra.api.dependencies.services import get_service
from mirumon.infra.api.dependencies.users.permissions import get_user_in_login
from mirumon.infra.api.users.http_endpoints.models.auth import (
    UserInLoginRequest,
    UserTokenInResponse,
)
from mirumon.resources import strings

router = APIRouter()


# TODO: remove scope, client_id, client_secret, gran_type
@router.post(
    "/users/token",
    name="users:token",
    summary="Get User Token",
    response_model=UserTokenInResponse,
)
async def login(
    user: UserInLoginRequest = Depends(get_user_in_login),
    users_service: AuthUsersService = Depends(get_service(AuthUsersService)),
) -> UserTokenInResponse:
    try:
        token_payload = await users_service.create_access_token(
            username=user.username, raw_password=user.password, scopes=user.scopes
        )
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=strings.INCORRECT_LOGIN_INPUT,
        )

    return UserTokenInResponse.parse_obj(token_payload)
