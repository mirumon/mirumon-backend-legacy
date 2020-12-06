from typing import List, Optional

from mirumon.application.users.users_repo import UserDoesNotExist
from mirumon.domain.users.entities import HashedPassword, User, UserID, Username
from mirumon.domain.users.scopes import Scopes
from mirumon.infra.components.postgres.repo import PostgresRepository
from mirumon.infra.infra_model import InfraModel

GET_USER_BY_USERNAME_QUERY = """
SELECT id,
       username,
       salt,
       hashed_password,
       scopes,
       created_at,
       updated_at
FROM users
WHERE username = $1
"""
CREATE_USER_QUERY = """
INSERT INTO users (username, salt, hashed_password, scopes)
VALUES ($1, $2, $3, $4)
RETURNING id, username, salt, hashed_password, scopes
"""


class UserInfraModel(InfraModel):
    id: Optional[UserID]
    username: Username
    scopes: List[Scopes]
    salt: str
    hashed_password: HashedPassword

    @classmethod
    def from_entity(cls, entity: User) -> "UserInfraModel":
        return cls.parse_obj(entity.dict())

    def to_entity(self) -> User:
        return User(**self.dict())


class UsersRepositoryImplementation(PostgresRepository):
    async def create(self, user: User) -> User:
        new_user = UserInfraModel.from_entity(user)

        async with self.connection.transaction():
            user_row = await self._log_and_fetch_row(
                CREATE_USER_QUERY,
                new_user.username,
                new_user.salt,
                str(new_user.hashed_password),
                new_user.scopes,
            )
            return User(**dict(user_row))

    async def get_user_by_username(self, *, username: str) -> User:
        user_row = await self._log_and_fetch_row(GET_USER_BY_USERNAME_QUERY, username)
        if user_row:
            return UserInfraModel(**user_row).to_entity()

        raise UserDoesNotExist(
            "user with username {0} does not exist".format(username),
        )
