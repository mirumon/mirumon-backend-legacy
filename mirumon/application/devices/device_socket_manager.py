from typing import Dict, List, Optional

from loguru import logger
from starlette.websockets import WebSocket

from mirumon.domain.devices.entities import DeviceID

Connections = Dict[DeviceID, WebSocket]

# TODO: move to infra or make protocol for device socket


class DevicesSocketManager:
    def __init__(self, sockets: Optional[Connections] = None) -> None:
        self._sockets = sockets or {}

    async def connect(self, device_id: DeviceID, websocket: WebSocket) -> None:
        await websocket.accept()
        socket = websocket
        self._sockets[device_id] = socket

    async def disconnect(self, device_id: DeviceID) -> None:
        try:
            socket = self._sockets.pop(device_id)
        except KeyError:
            logger.warning(f"device:{device_id} already disconnect")
        else:
            await socket.close()

    def get_client(self, device_id: DeviceID) -> WebSocket:
        return self._sockets[device_id]

    async def close(self) -> None:
        for socket in self._sockets.values():
            await socket.close()

    @property
    def client_ids(self) -> List[DeviceID]:
        return list(self._sockets.keys())

    def __str__(self) -> str:
        return f"DeviceSocketManager<{self._sockets}>"


socket_manager = DevicesSocketManager()
