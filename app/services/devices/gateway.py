from typing import Dict, List

from app.domain.device.base import DeviceID
from app.services.devices.client import DeviceClient
from app.settings.environments.base import AppSettings

Connections = Dict[DeviceID, DeviceClient]


class DeviceClientsGateway:
    def __init__(self, settings: AppSettings, clients: Connections) -> None:
        self.settings = settings
        self.clients = clients

    def add_client(self, client: DeviceClient) -> None:
        self.clients[client.device_id] = client

    def remove_client(self, client: DeviceClient) -> None:
        self.clients.pop(client.device_id)

    def get_client(self, device_id: DeviceID) -> DeviceClient:
        return self.clients[device_id]

    async def close(self) -> None:
        for client in self.clients.values():
            await client.close()

    @property
    def client_ids(self) -> List[DeviceID]:
        return list(self.clients.keys())
