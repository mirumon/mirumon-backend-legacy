from typing import Dict

from app.domain.device.base import DeviceUID
from app.services.devices.client import DeviceClient


class DeviceClientsGateWay:
    def __init__(self) -> None:
        self._clients: Dict[DeviceUID, DeviceClient] = {}

    def add_client(self, client: DeviceClient) -> None:
        self._clients[client.device_uid] = client

    def remove_client(self, client: DeviceClient) -> None:
        self._clients.pop(client.device_uid)

    def get_client(self, device_uid: DeviceUID) -> DeviceClient:
        return self._clients[device_uid]
