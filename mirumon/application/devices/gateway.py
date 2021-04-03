from typing import Dict, List

from loguru import logger
from starlette.websockets import WebSocket

from mirumon.domain.devices.entities import DeviceID
from mirumon.settings.environments.app import AppSettings

Connections = Dict[DeviceID, WebSocket]


class DeviceClientsManager:
    def __init__(self, settings: AppSettings, clients: Connections) -> None:
        self.settings = settings
        self.clients = clients

    async def connect(self, device_id: DeviceID, websocket: WebSocket) -> None:
        await websocket.accept()
        client = websocket
        self.clients[device_id] = client

    async def disconnect(self, device_id: DeviceID) -> None:
        try:
            client = self.clients.pop(device_id)
            await client.close()
        except KeyError:
            logger.warning(f"device:{device_id} already disconnect")

    def get_client(self, device_id: DeviceID) -> WebSocket:
        return self.clients[device_id]

    async def close(self) -> None:
        for client in self.clients.values():
            await client.close()

    @property
    def client_ids(self) -> List[DeviceID]:
        return list(self.clients.keys())
