import aio_pika
from loguru import logger

from mirumon.settings.environments.app import AppSettings


async def create_rabbit_connection(settings: AppSettings) -> aio_pika.Connection:
    logger.info(f"Connecting to RabbitMQ with DSN `{settings.rabbit_dsn}`")

    dsn = str(settings.rabbit_dsn)
    connection: aio_pika.Connection = await aio_pika.connect(dsn)

    logger.info("Connection to RabbitMQ established")
    return connection


async def close_rabbit_connection(connection: aio_pika.Connection) -> None:
    logger.info("Closing connection to RabbitMQ")

    await connection.close()  # type: ignore

    logger.info("Connection to RabbitMQ closed")
