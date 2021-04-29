from aioredis import Redis

from mirumon.application.devices.devices_socket_repo import DevicesSocketRepo
from mirumon.domain.devices.entities import DeviceID


class DevicesSocketRepoImpl(DevicesSocketRepo):
    def __init__(self, conn: Redis):
        self.conn = conn

    # TODO: add NX param and expire, when make heartbeat for sockets
    #  https://medium.com/hackernoon/enforcing-a-single-web-socket-connection-per-user-with-node-js-socket-io-and-redis-65f9eb57f66a
    async def set_connected(self, device_id: DeviceID) -> bool:
        return await self.conn.set(f"devices:{device_id}", "connected")

    async def set_disconnected(self, device_id: DeviceID) -> bool:
        return await self.conn.set(f"devices:{device_id}", "disconnected")

    # TODO: add scan to optimize search in list controller
    async def is_connected(self, device_id: DeviceID) -> bool:
        status = await self.conn.get(f"devices:{device_id}", encoding="utf-8")
        return status == "connected"
