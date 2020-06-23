import asyncio
import json
import uuid
from typing import Any, Dict, List, Set, Union, cast

import aioredis
from fastapi import HTTPException
from loguru import logger
from starlette import websockets

from app.domain.device.base import DeviceID
from app.domain.device.detail import DeviceOverview
from app.domain.event.base import EventInResponse, SyncID
from app.services.devices.client import DeviceClient
from app.settings.environments.base import AppSettings


class DeviceEventsRepository:
    def __init__(self, pool: aioredis.Redis) -> None:
        self.pool: aioredis.Redis = pool

    async def create_event(
        self, sync_id: SyncID, event_type: str, event_json: str
    ) -> Any:
        return await self.pool.hset(f"events:{sync_id}", event_type, event_json)

    async def get_event(
        self, device_uid: DeviceID, event_type: str
    ) -> Union[dict, list, str]:
        bytes_data = await self.pool.hget(f"device:{device_uid}", event_type)
        return json.loads(bytes_data.decode())

    async def get_event_for_all_devices(self, event_type: str) -> Any:
        async for key in self.pool.iscan(match="device:*"):
            event_value = await self.pool.hget(key, event_type)
            yield key, event_value

    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()


ABNORMAL_CLOSURE = 1006
TRY_AGAIN_LATER = 1013


class EventsService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self._registered_events: Set[SyncID] = set()
        self._events_responses: Dict[SyncID, EventInResponse] = {}
        self._asyncio_events: Dict[SyncID, asyncio.Event] = {}

    def register_event(self) -> SyncID:
        event_sync_id = cast(SyncID, uuid.uuid4())
        self._registered_events.add(event_sync_id)
        return event_sync_id

    def set_event_response(
        self, sync_id: SyncID, event_response: EventInResponse,
    ) -> None:
        if sync_id not in self._registered_events:
            logger.error(f"unregistered event with sync_id {sync_id}")
            raise KeyError("unregistered event")
        self._events_responses[sync_id] = event_response
        logger.debug(event_response)
        self._asyncio_events[sync_id].set()

    async def wait_event_from_client(self, sync_id: SyncID, client: DeviceClient):
        event = asyncio.Event()
        self._asyncio_events[sync_id] = event
        response_time = 5
        while not event.is_set():
            response_time -= 0.1
            try:
                await asyncio.wait_for(event.wait(), 0.1)
            except asyncio.TimeoutError:
                if not client.is_connected:
                    logger.error("client disconnected while waiting event")
                    raise websockets.WebSocketDisconnect(code=ABNORMAL_CLOSURE)
                if not response_time:
                    logger.warning("response timeout while waiting event")
                    raise websockets.WebSocketDisconnect(code=TRY_AGAIN_LATER)

        response = self.pop_event(sync_id)
        if response.error:
            raise HTTPException(status_code=503, detail=response.error.dict())
        return response.result

    def pop_event(self, sync_id: SyncID) -> EventInResponse:
        self._registered_events.remove(sync_id)
        self._asyncio_events.pop(sync_id)
        return self._events_responses.pop(sync_id)

    # old devices list
    async def send_bulk_event(self) -> List[DeviceOverview]:
        pass

        # for client in list(self._clients.values()):
        #     sync_id = events_manager.register_event()
        #     await client.send_event(
        #         EventInRequest(method=DeviceEventType.list, sync_id=sync_id)
        #     )
        #     try:
        #         device = await events_manager.wait_event_from_client(
        #             sync_id=sync_id, client=client
        #         )
        #     except (WebSocketDisconnect, ValidationError) as error:
        #         logger.debug(f"device client skipped in list event. error: {error}")
        #         continue
        #     else:
        #         devices.append(
        #             DeviceOverview(uid=client.device_id, online=True, **device)
        #         )
        # return devices
