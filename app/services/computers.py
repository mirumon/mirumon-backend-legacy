from typing import Dict, List

from app.services.clients import Client


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[str, Client] = {}

    def add_client(self, client: Client) -> None:
        self._clients[client.mac_address] = client

    def remove_client(self, client: Client) -> None:
        self._clients.pop(client.mac_address)

    def get_client(self, mac_address: str) -> Client:
        return self._clients[mac_address]

    @property
    def clients(self) -> List[Client]:
        return list(self._clients.values())


_clients_manager = ClientsManager()


def get_clients_manager() -> ClientsManager:
    return _clients_manager
