from aio_pika import connect
from aio_pika.connection import Connection
from fastapi import FastAPI
from loguru import logger

from mirumon.settings.environments.app import AppSettings


async def create_rabbit_connection(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to {0}", settings.rabbit_dsn)

    dsn = str(settings.rabbit_dsn)
    connection: Connection = await connect(dsn)

    # add to app state to use later
    app.state.rabbit_conn = connection

    logger.info("Connection established")


async def close_rabbit_connection(app: FastAPI) -> None:
    logger.info("Closing connection to rabbit")

    connection = app.state.rabbit_conn
    await connection.close()

    logger.info("Connection closed")
