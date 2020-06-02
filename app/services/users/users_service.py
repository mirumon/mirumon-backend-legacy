from app.components.config import APPSettings
from app.database.errors import EntityDoesNotExist
from app.database.repositories.users_repo import UsersRepository
from app.domain.user.jwt import UserToken
from app.domain.user.user import User
from app.services.users import jwt


class UsersService:
    users_repo: UsersRepository
    secret_key: str
    jwt_token_type: str

    def __init__(self, users_repo: UsersRepository, settings: APPSettings):
        self.users_repo = users_repo
        self.secret_key = str(settings.secret_key)
        self.jwt_token_type = settings.jwt_token_type

    async def register_new_user(self, user) -> None:
        if await self.users_repo.check_username_is_taken(user.username):
            raise RuntimeError("username is taken")
        await self.users_repo.create_user(**user.dict())

    async def login_user(self, user) -> None:
        try:
            await self.users_repo.check_user_credentials(user)
        except ValueError:
            raise RuntimeError("incorrect password")

    def create_access_token_for_user(self, user):
        token = jwt.create_access_token_for_user(user, self.secret_key)
        return UserToken(access_token=token, token_type=self.jwt_token_type)

    async def find_user_by_token(self, token: str, secret_key: str):
        try:
            stored_user = jwt.get_user_from_token(token, secret_key)
        except ValueError:
            raise RuntimeError("token decode error")

        try:
            return await self.users_repo.get_user_by_username(
                username=stored_user.username
            )
        except EntityDoesNotExist:
            raise RuntimeError("user does not exist")

    async def check_user_scopes(self, user: User, security_scopes):
        return not all(scope in user.scopes for scope in security_scopes.scopes)
