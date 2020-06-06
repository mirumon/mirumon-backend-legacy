from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.api.dependencies.services import get_users_service
from app.api.dependencies.user_auth import check_user_scopes, get_user_in_login
from app.domain.user.scopes import AdministrationScopes
from app.domain.user.user import UserInCreate, UserInLogin, UserToken
from app.resources import strings
from app.services.users.users_service import UsersService

router = APIRouter()


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    name="auth:register",
    dependencies=[Depends(check_user_scopes([AdministrationScopes.edit]))],
)
async def register(
    user_create: UserInCreate, users_service: UsersService = Depends(get_users_service),
) -> None:
    try:
        await users_service.register_new_user(user_create.username)
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN
        )


# TODO: remove scope, client_id, client_secret, gran_type
@router.post("/login", response_model=UserToken, name="auth:login")
async def login(
    user: UserInLogin = Depends(get_user_in_login),
    users_service: UsersService = Depends(get_users_service),
) -> UserToken:
    try:
        return await users_service.login_user(user)
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=strings.INCORRECT_LOGIN_INPUT
        )
