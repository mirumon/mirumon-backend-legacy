from fastapi import FastAPI
from loguru import logger

from mirumon.application.devices.gateway import Connections, DeviceClientsManager
from mirumon.settings.environments.app import AppSettings


def create_devices_connections(app: FastAPI, settings: AppSettings) -> None:
    logger.info("Initialize connections for devices")

    logger.info("Connections initialized")


async def close_devices_connections(app: FastAPI) -> None:
    logger.info("Closing connections to devices")

    # await app.state.gateway.close()

    logger.info("Connections closed")
