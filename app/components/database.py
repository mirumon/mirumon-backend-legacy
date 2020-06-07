import asyncpg
from fastapi import FastAPI
from loguru import logger

from app.components.config import APPSettings
from app.database.repositories.users_repo import UsersRepository


async def create_db_connection(app: FastAPI, settings: APPSettings) -> None:
    dsn = str(settings.database_dsn)
    logger.info("Connecting to {0}", dsn)

    app.state.pool = await asyncpg.create_pool(dsn)

    logger.info("Connection established")


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.pool.close()

    logger.info("Connection closed")


# TODO remove after refactoring
async def create_superuser(app: FastAPI, settings: APPSettings) -> None:
    async with app.state.pool.acquire() as conn:
        repo = UsersRepository(conn)
        try:
            await repo.create_user(username=settings.first_superuser, scopes=settings.initial_superuser_scopes, password=settings.first_superuser_password)
        except:
            pass