from asyncpg import UniqueViolationError
from loguru import logger

from mirumon.application.users.users_repo import UserDoesNotExist, UsersRepository
from mirumon.domain.users.entities import HashedPassword, User, Username
from mirumon.domain.users.scopes import Scopes


class UsersService:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def create_new_user(
        self,
        username: Username,
        scopes: Scopes,
        salt: str,
        hashed_password: HashedPassword,
    ) -> User:

        user_id = User.generate_id()
        user = User(
            id=user_id,
            username=username,
            scopes=scopes,
            salt=salt,
            hashed_password=hashed_password,
        )
        try:
            return await self.users_repo.create(user)
        except UniqueViolationError:
            raise RuntimeError("username is already exists")

    async def find_user_by_username(self, username: Username) -> User:
        try:
            user_db = await self.users_repo.get_user_by_username(username=username)
        except UserDoesNotExist:
            logger.debug("user does not exist")
            raise RuntimeError("user does not exist")

        return User(**user_db.dict())
