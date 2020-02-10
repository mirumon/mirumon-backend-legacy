import json
from typing import Any, Union

import aioredis

from app.models.domain.types import DeviceUID


class EventsRepo:
    def __init__(self, connection: aioredis.Redis) -> None:
        self.pool: aioredis.Redis = connection

    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()

    async def set_event_for_device(
        self, device_uid: DeviceUID, event_type: str, event_json: str
    ) -> Any:
        return await self.pool.hset(f"device:{device_uid}", event_type, event_json)

    async def get_event_for_device(
        self, device_uid: DeviceUID, event_type: str
    ) -> Union[dict, list, str]:
        bytes_data = await self.pool.hget(f"device:{device_uid}", event_type)
        return json.loads(bytes_data.decode())

    async def get_event_for_all_devices(self, event_type: str) -> Any:
        async for key in self.pool.iscan(match="device:*"):
            event_value = await self.pool.hget(key, event_type)
            yield key, event_value
