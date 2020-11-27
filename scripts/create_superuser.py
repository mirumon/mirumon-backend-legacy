#!/usr/bin/env python

import asyncio
import sys

import asyncpg
import bcrypt
from asyncpg import Connection
from asyncpg.transaction import Transaction
from passlib.context import CryptContext

from mirumon.domain.users.scopes import DevicesScopes, UsersScopes
from mirumon.infra.users.users_repo import UsersRepository


async def create_superuser(
    postgres_dsn: str, superuser_username: str, superuser_password: str
) -> None:
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
