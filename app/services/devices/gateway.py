from typing import Dict

from app.domain.device.base import DeviceID
from app.services.devices.client import DeviceClient


class DeviceClientsGateway:
    def __init__(self, clients: Dict[DeviceID, DeviceClient]) -> None:
        self.clients = clients

    def add_client(self, client: DeviceClient) -> None:
        self.clients[client.device_id] = client

    def remove_client(self, client: DeviceClient) -> None:
        self.clients.pop(client.device_id)

    def get_client(self, device_uid: DeviceID) -> DeviceClient:
        return self.clients[device_uid]

    async def close(self) -> None:
        for client in self.clients.values():
            await client.close()
