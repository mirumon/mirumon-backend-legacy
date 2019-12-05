from typing import Dict, List

from app.services.clients import Client, DeviceID


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[DeviceID, Client] = {}

    def add_client(self, client: Client) -> None:
        self._clients[client.device_id] = client

    def remove_client(self, client: Client) -> None:
        self._clients.pop(client.device_id)

    def get_client(self, device_id: DeviceID) -> Client:
        return self._clients[device_id]

    @property
    def clients(self) -> List[Client]:
        return list(self._clients.values())


_clients_manager = ClientsManager()


def get_clients_manager() -> ClientsManager:
    return _clients_manager