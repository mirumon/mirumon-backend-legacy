from typing import List
from uuid import UUID

from app.db.repositories.base import BaseRepository
from app.models.domain.groups import Group
from app.models.domain.users import User

GET_USER_GROUPS_QUERY = """
SELECT id, name
FROM device_groups
WHERE user_id = (SELECT id FROM users WHERE username = $1)
"""
CREATE_NEW_GROUP_QUERY = """
INSERT INTO device_groups (name, user_id)
VALUES ($1, (SELECT id FROM users WHERE username = $2))
"""


class GroupsRepository(BaseRepository):
    async def get_user_groups(self, *, user: User) -> List[Group]:
        rows = await self._log_and_fetch(GET_USER_GROUPS_QUERY, user.username)
        return [Group(id=row["id"], name=row["name"], owner=user) for row in rows]

    async def create_new_group_for_user(self, *, name: str, user: User) -> None:
        await self._log_and_execute(CREATE_NEW_GROUP_QUERY, name, user.username)
