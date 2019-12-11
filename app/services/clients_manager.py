from typing import Dict, List

from loguru import logger

from app.models.schemas.events.rest import DeviceID
from app.services.clients import Client


class ClientsManager:
    def __init__(self) -> None:
        self._clients: Dict[DeviceID, Client] = {}

    def add_client(self, client: Client) -> None:
        self._clients[client.device_id] = client
        logger.error(self._clients)

    def remove_client(self, client: Client) -> None:
        self._clients.pop(client.device_id)

    def get_client(self, device_id: DeviceID) -> Client:
        logger.error(f"get client: {self._clients[device_id]}")
        return self._clients[device_id]

    @property
    def clients(self) -> List[Client]:
        return list(self._clients.values())
