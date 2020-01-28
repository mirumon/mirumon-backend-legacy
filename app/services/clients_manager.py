from typing import Dict, List

from app.models.schemas.events.types import DeviceUID
from app.services.clients import Client


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[DeviceUID, Client] = {}

    def add_client(self, client: Client) -> None:
        self._clients[client.device_uid] = client

    def remove_client(self, client: Client) -> None:
        self._clients.pop(client.device_uid)

    def get_client(self, device_uid: DeviceUID) -> Client:
        return self._clients[device_uid]

    @property
    def clients(self) -> List[Client]:
        return list(self._clients.values())
