from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.db.errors import EntityDoesNotExist
from app.domain.user.jwt import JWTToken
from app.services.users.users_service import UsersService
from old_app.api.dependencies.authentication import check_user_scopes_requirements
from old_app.common import strings
from app.settings.environments import config
from old_app.models.domain.scopes import AdministrationScopes
from old_app.models.schemas.users import UserInCreate
from old_app.services import jwt

router = APIRouter()


@router.post("/login", response_model=JWTToken, name="auth:login")
async def login(
    user_login: OAuth2PasswordRequestForm = Depends(),
    users_service: UsersService = Depends(get_service(UsersService)),
) -> JWTToken:
    wrong_login_error = HTTPException(
        status_code=HTTP_400_BAD_REQUEST, detail=strings.INCORRECT_LOGIN_INPUT
    )

    try:
        user = await users_repo.get_user_by_username(username=user_login.username)
    except EntityDoesNotExist as existence_error:
        raise wrong_login_error from existence_error

    if not user.check_password(user_login.password):
        raise wrong_login_error

    token = jwt.create_access_token_for_user(user, str(config.SECRET_KEY))
    return JWTToken(access_token=token, token_type=config.JWT_TOKEN_TYPE)


@router.post(
    "",
    status_code=HTTP_201_CREATED,
    name="auth:register",
    dependencies=[Depends(check_user_scopes_requirements([AdministrationScopes.edit]))],
)
async def register(
    user_create: UserInCreate,
    users_service: UsersService = Depends(get_service(UsersService)),
) -> None:
    try:
        await users_service.register_new_user(user_create.username)
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN
        )
