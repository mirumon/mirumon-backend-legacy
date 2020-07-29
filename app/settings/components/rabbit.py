from aio_pika import ExchangeType, connect
from fastapi import FastAPI
from loguru import logger

from app.settings.environments.base import AppSettings


async def create_rabbit_connection(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Connecting to {0}", settings.rabbit_dsn)

    dsn = str(settings.rabbit_dsn)
    connection = await connect(dsn)

    channel = await connection.channel()

    # Configure exchange for pushing events to all consumers (http views)
    exchange = await channel.declare_exchange("events", ExchangeType.FANOUT)

    # Declare a queue and disable saving messages,
    # since messages have a small life cycle and we can save memory
    queue = await channel.declare_queue(exclusive=True, durable=False)
    await queue.bind(exchange)

    # add to app state to use later
    app.state.rabbit_conn = connection
    app.state.rabbit_channel = channel
    app.state.rabbit_queue = queue
    app.state.rabbit_exchange = exchange

    logger.info("Connection established")


async def close_rabbit_connection(app: FastAPI) -> None:
    logger.info("Closing connection to rabbit")

    connection = app.state.rabbit_conn
    await connection.close()

    logger.info("Connection closed")
