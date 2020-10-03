from fastapi import Depends
from starlette.datastructures import State

from app.api.dependencies.state import get_state
from app.services.devices.gateway import Connections, DeviceClientsManager
from app.settings.config import get_app_settings
from app.settings.environments.base import AppSettings


def _get_device_connections(state: State = Depends(get_state)) -> Connections:
    """Connections state for websockets for devices."""
    return state.device_connections


def get_device_clients_manager(
    settings: AppSettings = Depends(get_app_settings),
    clients: Connections = Depends(_get_device_connections),
) -> DeviceClientsManager:
    return DeviceClientsManager(settings=settings, clients=clients)
