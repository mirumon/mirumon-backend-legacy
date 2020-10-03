import asyncio
import sys

import asyncpg
from asyncpg import Connection
from asyncpg.transaction import Transaction
from passlib.context import CryptContext
import bcrypt

from app.database.repositories.users_repo import UsersRepository
from app.domain.user.scopes import DevicesScopes, UsersScopes


async def create_superuser(postgres_dsn, superuser_username: str, superuser_password: str):
    conn: Connection = await asyncpg.connect(postgres_dsn)

    transaction: Transaction = conn.transaction()
    await transaction.start()
    repo = UsersRepository(conn)
    salt = bcrypt.gensalt().decode()
    password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(
        salt + superuser_password
    )
    await repo.create(
        username=superuser_username,
        salt=salt,
        password=password,
        scopes=[
            DevicesScopes.write,
            DevicesScopes.read,
            UsersScopes.read,
            UsersScopes.write,
        ],
    )
    await transaction.commit()
    await conn.close()


def run() -> None:
    loop = asyncio.get_event_loop()
    username, password = sys.argv[1:3]
    try:
        postgres_dsn = sys.argv[4]
    except IndexError:
        postgres_dsn = "postgres://postgres:postgres@localhost:5432/postgres"
    try:
        task = create_superuser(postgres_dsn, username, password)
        asyncio.run(task)
    finally:
        loop.close()


if __name__ == "__main__":
    run()
