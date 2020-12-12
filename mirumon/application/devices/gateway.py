from typing import Dict, List

from starlette.websockets import WebSocket

from mirumon.application.devices.client import DeviceClient
from mirumon.domain.devices.entities import DeviceID
from mirumon.settings.environments.app import AppSettings

Connections = Dict[DeviceID, DeviceClient]


class DeviceClientsManager:
    def __init__(self, settings: AppSettings, clients: Connections) -> None:
        self.settings = settings
        self.clients = clients

    async def connect(self, device_id: DeviceID, websocket: WebSocket) -> DeviceClient:
        await websocket.accept()
        client = DeviceClient(device_id=device_id, websocket=websocket)
        self.clients[device_id] = client
        return client

    async def disconnect(self, device_id: DeviceID) -> None:
        client = self.clients.pop(device_id)
        await client.close()

    def get_client(self, device_id: DeviceID) -> DeviceClient:
        return self.clients[device_id]

    async def close(self) -> None:
        for client in self.clients.values():
            await client.close()

    @property
    def client_ids(self) -> List[DeviceID]:
        return list(self.clients.keys())
