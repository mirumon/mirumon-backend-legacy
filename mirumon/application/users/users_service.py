from asyncpg import UniqueViolationError
from loguru import logger

from mirumon.domain.users.entities import HashedPassword, User, Username
from mirumon.infra.api.endpoints.users.http.models.crud import UserInCreateRequest
from mirumon.infra.errors import EntityDoesNotExist
from mirumon.infra.users.users_repo import UsersRepository


class UsersService:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def create_new_user(
        self, user: UserInCreateRequest, salt: str, hashed_password: HashedPassword
    ) -> User:
        try:
            return await self.users_repo.create(
                username=user.username,
                salt=salt,
                password=hashed_password,
                scopes=user.scopes,
            )
        except UniqueViolationError:
            raise RuntimeError("username is already exists")

    async def find_user_by_username(self, username: Username) -> User:
        try:
            user_db = await self.users_repo.get_user_by_username(username=username)
        except EntityDoesNotExist:
            logger.debug("user does not exist")
            raise RuntimeError("user does not exist")

        return User(**user_db.dict())
