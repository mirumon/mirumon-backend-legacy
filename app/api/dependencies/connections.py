from typing import Optional

from fastapi import Depends
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.services.devices.gateway import Connections, DeviceClientsGateway
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def _get_device_clients(request: Request) -> Connections:
    """Connections state for websockets for devices."""
    return request.app.state.device_connections


def _get_device_clients_ws(websocket: WebSocket) -> Connections:
    """Connections state for websockets for devices."""
    return websocket.app.state.device_connections


def get_clients_gateway(
    settings: AppSettings = Depends(get_app_settings),
    clients: Connections = Depends(_get_device_clients),
) -> DeviceClientsGateway:
    return DeviceClientsGateway(settings=settings, clients=clients)


def get_clients_gateway_ws(
    settings: AppSettings = Depends(get_app_settings),
    clients: Connections = Depends(_get_device_clients_ws),
) -> DeviceClientsGateway:
    return DeviceClientsGateway(settings=settings, clients=clients)
