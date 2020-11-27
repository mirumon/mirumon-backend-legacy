from fastapi import Depends
from starlette.datastructures import State

from mirumon.application.devices.gateway import Connections, DeviceClientsManager
from mirumon.infra.api.dependencies.state import get_state
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.base import AppSettings


def _get_device_connections(state: State = Depends(get_state)) -> Connections:
    """Connections state for websockets for devices."""
    return state.device_connections


def get_device_clients_manager(
    settings: AppSettings = Depends(get_app_settings),
    clients: Connections = Depends(_get_device_connections),
) -> DeviceClientsManager:
    return DeviceClientsManager(settings=settings, clients=clients)
