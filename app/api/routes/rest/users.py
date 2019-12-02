from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.api.dependencies.authentication import check_user_scopes_requirements
from app.api.dependencies.database import get_repository
from app.common import config, strings
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.models.domain.scopes import AdministrationScopes
from app.models.schemas.jwt import JWTToken
from app.models.schemas.users import UserInCreate
from app.services import authentication, jwt

router = APIRouter()


@router.post("/login", response_model=JWTToken, name="auth:login")
async def login(
    user_login: OAuth2PasswordRequestForm = Depends(),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
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
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> None:
    if await authentication.check_username_is_taken(users_repo, user_create.username):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN
        )

    await users_repo.create_user(**user_create.dict())
