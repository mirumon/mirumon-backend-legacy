import uuid
from abc import ABCMeta
from types import MappingProxyType
from typing import List, Optional, Type, Union

from loguru import logger
from pydantic import BaseModel, parse_obj_as

from app.api.models.ws.events.events import (
    EventID,
    EventInRequest,
    EventInResponse,
    EventParams,
    EventResult,
)
from app.api.models.ws.events.types import EventTypes
from app.database.models.device import detail, hardware, software
from app.database.repositories.events_repo import EventProcessError, EventsRepository
from app.domain.devices.base import DeviceID
from app.services.devices.gateway import DeviceClientsManager


class EventsService:
    def __init__(
        self,
        events_repo: EventsRepository,
        gateway: DeviceClientsManager,  # todo: move to proxy class
    ) -> None:
        self.events_repo = events_repo
        self.gateway = gateway

    async def send_event_request(
        self,
        device_id: DeviceID,
        event_type: EventTypes,
        params: Optional[EventParams] = None,
    ) -> EventID:
        event_id = EventID(uuid.uuid4())
        event = EventInRequest(id=event_id, method=event_type, params=params)
        try:
            client = self.gateway.get_client(device_id)
        except KeyError:
            logger.debug(f"client for device:{device_id} not found")
            raise RuntimeError
        await client.send_event(event)

        return event.id

    async def send_event_response(self, event: EventInResponse) -> None:
        await self.events_repo.publish_event_response(event)

    async def listen_event(
        self,
        event_id: EventID,
        event_type: EventTypes,
        process_timeout: Optional[int] = None,
    ) -> EventResult:
        try:
            event_payload = await self.events_repo.process_event(
                event_id, process_timeout
            )
        except EventProcessError as error:
            logger.error(f"event error:{error}")
            raise RuntimeError
        event_model = _get_model_for_event(event_type)
        return parse_obj_as(event_model, event_payload)  # type: ignore


def _get_model_for_event(event_type: EventTypes) -> Union[Type[BaseModel], ABCMeta]:
    return _EVENT_MAPPER[event_type]


_EVENT_MAPPER = MappingProxyType(
    {
        EventTypes.detail: detail.DeviceInfo,
        EventTypes.hardware: hardware.HardwareModel,
        EventTypes.software: List[software.InstalledProgram],
        EventTypes.shutdown: dict,
    }
)
