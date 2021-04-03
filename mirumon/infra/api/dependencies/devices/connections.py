from fastapi import Depends
from starlette.datastructures import State

from mirumon.application.devices.gateway import Connections, DeviceClientsManager, \
    conn_manager
from mirumon.infra.api.dependencies.state import get_state
from mirumon.settings.config import get_app_settings
from mirumon.settings.environments.app import AppSettings


def get_device_clients_manager() -> DeviceClientsManager:
    return conn_manager
