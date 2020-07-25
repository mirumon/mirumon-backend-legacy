import json
import uuid
from datetime import timedelta
from typing import Tuple

import aioredis

from app.domain.device.base import DeviceID
from app.settings.components.jwt import create_jwt_token
from app.settings.environments.base import AppSettings


class DevicesRepository:
    """Redis storage implementation for devices' events."""

    def __init__(self, settings: AppSettings, pool: aioredis.Redis) -> None:
        self.settings = settings
        self.pool: aioredis.Redis = pool

    async def create_device(self):
        device_id = uuid.uuid4()
        content = {"device_id": str(device_id)}
        secret_key = self.settings.secret_key.get_secret_value()
        delta = timedelta(days=365)
        token = create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=delta
        )
        await self.pool.hset(f"devices:{device_id}", "is_online", 0)
        return token

    async def set_event(
        self, device_id: DeviceID, event_type: str, event_json: str
    ) -> None:
        await self.pool.hset(f"devices:{device_id}", event_type, event_json)

    async def get_event(self, device_id: DeviceID, event_type: str) -> dict:
        bytes_data = await self.pool.hget(f"device:{device_id}", event_type)
        return json.loads(bytes_data.decode())

    async def set_online(self, device_id: DeviceID) -> None:
        await self.pool.hset(f"devices:{device_id}", "is_online", 1)

    async def set_offline(self, device_id: DeviceID) -> None:
        await self.pool.hset(f"devices:{device_id}", "is_online", 0)

    async def is_online(self, device_id: DeviceID) -> bool:
        status = self.pool.hget(f"devices:{device_id}", "is_online")
        return bool(status)

    async def get_event_for_all_devices(self, event_type: str) -> Tuple[DeviceID, dict]:
        async for key in self.pool.iscan(match="devices:*"):
            event_value = await self.pool.hget(key, event_type)
            yield key, event_value
