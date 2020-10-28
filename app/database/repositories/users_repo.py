from typing import List, Optional

from app.api.models.http.users.users import UserInUpdate
from app.database.errors import EntityDoesNotExist
from app.database.models.base import ModelDB
from app.database.repositories.protocols.base import PostgresRepository
from app.domain.users.scopes import Scopes
from app.domain.users.user import HashedPassword, User, UserID, Username

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
UPDATE_USER_QUERY = """
UPDATE users
SET username        = $1,
    salt            = $2,
    hashed_password = $3,
    scopes          = $4
WHERE username = $7
RETURNING username, salt, hashed_password, scopes
"""


class UserInDB(ModelDB):
    id: Optional[UserID]
    username: Username
    scopes: List[Scopes]
    salt: str
    hashed_password: HashedPassword


class UsersRepository(PostgresRepository):
    async def create(
        self,
        *,
        username: Username,
        salt: str,
        password: HashedPassword,
        scopes: List[Scopes],
    ) -> User:
        new_user = UserInDB(
            username=username, scopes=scopes, salt=salt, hashed_password=password
        )

        async with self.connection.transaction():
            user_row = await self._log_and_fetch_row(
                CREATE_USER_QUERY,
                new_user.username,
                new_user.salt,
                str(new_user.hashed_password),
                new_user.scopes,
            )
            return User(**dict(user_row))

    async def update_user(
        self,
        *,
        user_in_db: UserInDB,
        user: UserInUpdate,
    ) -> UserInDB:

        user_in_db.username = user.username or user_in_db.username
        user_in_db.scopes = user.scopes or user_in_db.scopes

        async with self.connection.transaction():
            user_in_db = await self._log_and_fetch_row(
                UPDATE_USER_QUERY,
                user_in_db.username,
                user_in_db.salt,
                user_in_db.hashed_password,
                user_in_db.scopes,
                user.username,
            )

        return UserInDB.parse_obj(user_in_db)

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user_row = await self._log_and_fetch_row(GET_USER_BY_USERNAME_QUERY, username)
        if user_row:
            return UserInDB(**user_row)

        raise EntityDoesNotExist(
            "user with username {0} does not exist".format(username),
        )
