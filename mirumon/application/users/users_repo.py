from mirumon.application.repo_protocol import Repository
from mirumon.domain.users.entities import User


class UserDoesNotExist(Exception):
    """Raised when user was not found in infra layer."""


class UsersRepository(Repository):
    async def create(self, user: User) -> User:
        raise NotImplementedError

    async def get_user_by_username(self, *, username: str) -> User:
        raise NotImplementedError
