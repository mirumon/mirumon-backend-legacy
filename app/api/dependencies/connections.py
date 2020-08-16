from fastapi import Depends
from starlette.requests import HTTPConnection

from app.services.devices.gateway import Connections, DeviceClientsGateway
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def _get_device_clients(conn: HTTPConnection) -> Connections:
    """Connections state for devices."""
    return conn.app.state.device_connections


def get_clients_gateway(
    settings: AppSettings = Depends(get_app_settings),
    clients: Connections = Depends(_get_device_clients),
) -> DeviceClientsGateway:
    return DeviceClientsGateway(settings=settings, clients=clients)
