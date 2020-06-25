import uuid
from datetime import timedelta

import aioredis

from app.domain.device.base import DeviceID
from app.domain.event.base import SyncID
from app.settings.environments.base import AppSettings


class EventsRepository:
    def __init__(self, settings: AppSettings, pool: aioredis.Redis) -> None:
        self.settings = settings
        self.pool: aioredis.Redis = pool
        self.expire_timeout = timedelta(hours=2).seconds

    async def register_event(self, device_id: DeviceID, event_type: str) -> SyncID:
        event_sync_id = uuid.uuid4()
        key = f"events:{event_sync_id}"

        await self.pool.hsetnx(key, "event", event_type)
        await self.pool.hsetnx(key, "device", device_id)
        await self.pool.expire(key, self.expire_timeout)

        return SyncID(event_sync_id)

    async def is_event_registered(self, sync_id: SyncID) -> bool:
        return bool(await self.pool.exists(sync_id))
