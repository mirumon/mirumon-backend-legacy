from app.database.repositories.users_repo import UsersRepository


class UsersService:
    users_repo: UsersRepository

    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def register_new_user(self, user) -> None:
        if await self.users_repo.check_username_is_taken(user.username):
            raise RuntimeError("username is taken")
        await self.users_repo.create_user(**user.dict())
