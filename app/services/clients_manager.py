from typing import Dict, List

from app.models.domain.types import DeviceUID
from app.services.clients import DeviceClient


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[DeviceUID, DeviceClient] = {}

    def add_client(self, client: DeviceClient) -> None:
        self._clients[client.device_uid] = client

    def remove_client(self, client: DeviceClient) -> None:
        self._clients.pop(client.device_uid)

    def get_client(self, device_uid: DeviceUID) -> DeviceClient:
        return self._clients[device_uid]

    @property
    def clients(self) -> List[DeviceClient]:
        return list(self._clients.values())
