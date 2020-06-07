from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.api.dependencies.services import get_users_service
from app.api.dependencies.user_auth import check_user_scopes, get_user_in_login
from app.domain.user.scopes import AdministrationScopes
from app.domain.user.user import Token, User, UserInCreate, UserInLogin
from app.resources import strings
from app.services.users.users_service import UsersService

router = APIRouter()


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    name="auth:register",
    response_model=User,
    dependencies=[Depends(check_user_scopes([AdministrationScopes.edit]))],
)
async def register(
    new_user: UserInCreate, users_service: UsersService = Depends(get_users_service),
) -> None:
    try:
        return await users_service.register_new_user(new_user)
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN
        )


# TODO: remove scope, client_id, client_secret, gran_type
@router.post("/login", response_model=Token, name="auth:login")
async def login(
    user: UserInLogin = Depends(get_user_in_login),
    users_service: UsersService = Depends(get_users_service),
) -> Token:
    try:
        return await users_service.login_user(user)
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=strings.INCORRECT_LOGIN_INPUT
        )
