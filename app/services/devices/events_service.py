import uuid
from asyncio.exceptions import TimeoutError

from loguru import logger

from app.database.repositories.events_repo import EventsRepository
from app.domain.device.typing import DeviceID
from app.domain.event.base import EventInRequest, EventInResponse
from app.domain.event.types import EventTypes
from app.domain.event.typing import EventParams, SyncID
from app.services.devices.gateway import DeviceClientsGateway
from app.settings.environments.base import AppSettings


class EventsService:
    def __init__(
        self,
        settings: AppSettings,
        events_repo: EventsRepository,
        gateway: DeviceClientsGateway,
    ) -> None:
        self.settings = settings
        self.events_repo = events_repo
        self.gateway = gateway

    async def send_event_request(
        self, device_id: DeviceID, event_type: EventTypes, params: EventParams
    ) -> SyncID:
        sync_id = SyncID(uuid.uuid4())
        event = EventInRequest(sync_id=sync_id, method=event_type, params=params)
        try:
            client = self.gateway.get_client(device_id)
        except KeyError:
            logger.debug("client for device:{0} not found", device_id)
            raise RuntimeError
        await client.send_event(event)

        return event.sync_id

    async def send_event_response(self, event: EventInResponse) -> None:
        await self.events_repo.publish_event_response(event)

    async def listen_event(self, event_id: SyncID) -> EventInResponse:
        try:
            return await self.events_repo.process_event(event_id)
        except TimeoutError:
            raise RuntimeError
