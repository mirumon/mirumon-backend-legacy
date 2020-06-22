from typing import Dict

from app.domain.device.base import DeviceID
from app.services.devices.client import DeviceClient


class DeviceClientsGateway:
    def __init__(self) -> None:
        self._clients: Dict[DeviceID, DeviceClient] = {}

    def add_client(self, client: DeviceClient) -> None:
        self._clients[client.device_uid] = client

    def remove_client(self, client: DeviceClient) -> None:
        self._clients.pop(client.device_uid)

    def get_client(self, device_uid: DeviceID) -> DeviceClient:
        return self._clients[device_uid]
