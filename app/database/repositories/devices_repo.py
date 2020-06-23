import json
import uuid
from typing import Tuple

import aioredis

from app.domain.device.base import DeviceID


class DevicesRepository:
    """Redis storage implementation for devices' events."""

    def __init__(self, pool: aioredis.Redis) -> None:
        self.pool: aioredis.Redis = pool

    async def create_device(self):
        device_id = uuid.uuid4()
        await self.pool.hset(f"devices:{device_id}")

    async def set_event(
        self, device_id: DeviceID, event_type: str, event_json: str
    ) -> None:
        await self.pool.hset(f"devices:{device_id}", event_type, event_json)

    async def get_event(self, device_id: DeviceID, event_type: str) -> dict:
        bytes_data = await self.pool.hget(f"device:{device_id}", event_type)
        return json.loads(bytes_data.decode())

    async def get_event_for_all_devices(self, event_type: str) -> Tuple[DeviceID, dict]:
        async for key in self.pool.iscan(match="devices:*"):
            event_value = await self.pool.hget(key, event_type)
            yield key, event_value
