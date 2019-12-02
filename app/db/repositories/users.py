from typing import List, Optional

from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository
from app.models.domain.users import User, UserInDB

GET_USER_BY_EMAIL_QUERY = """
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
RETURNING id, created_at, updated_at
"""
UPDATE_USER_QUERY = """
UPDATE users
SET username        = $1,
    salt            = $2,
    hashed_password = $3,
    scopes          = $4
WHERE username = $7
RETURNING updated_at
"""


class UsersRepository(BaseRepository):
    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user_row = await self._log_and_fetch_row(GET_USER_BY_USERNAME_QUERY, username)
        if user_row:
            return UserInDB(**user_row)

        raise EntityDoesNotExist(
            "user with username {0} does not exist".format(username)
        )

    async def create_user(
        self, *, username: str, scopes: List[str], password: str
    ) -> UserInDB:
        user = UserInDB(username=username, scopes=scopes)
        user.change_password(password)

        async with self.connection.transaction():
            user_row = await self._log_and_fetch_row(
                CREATE_USER_QUERY,
                user.username,
                user.salt,
                user.hashed_password,
                user.scopes,
            )

        return user.copy(update=dict(user_row))

    async def update_user(  # noqa: WPS211
        self,
        *,
        user: User,
        username: Optional[str] = None,
        password: Optional[str] = None,
        scopes: Optional[List[str]] = None,
    ) -> UserInDB:
        user_in_db = await self.get_user_by_username(username=user.username)

        user_in_db.username = username or user_in_db.username
        user_in_db.scopes = scopes or user_in_db.scopes
        if password:
            user_in_db.change_password(password)

        async with self.connection.transaction():
            user_in_db.updated_at = await self._log_and_fetch_row(
                UPDATE_USER_QUERY,
                user_in_db.username,
                user_in_db.salt,
                user_in_db.hashed_password,
                user_in_db.scopes,
                user.username,
            )

        return user_in_db
