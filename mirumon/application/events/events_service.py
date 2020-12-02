import uuid
from types import MappingProxyType
from typing import Dict, List, Optional, Type, Union

from loguru import logger
from pydantic import parse_obj_as

from mirumon.application.devices.gateway import DeviceClientsManager
from mirumon.application.events.events_repo import EventProcessError, EventsRepository
from mirumon.application.events.models import (
    EventID,
    EventInRequest,
    EventInResponse,
    EventParams,
    EventResult,
    EventTypes,
)
from mirumon.domain.devices.entities import DeviceID
from mirumon.domain.events.device_detail import DeviceDetail
from mirumon.domain.events.device_hardware import DeviceHardware
from mirumon.domain.events.device_software import InstalledProgram


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
        *,
        process_timeout: Optional[int] = None,
    ) -> EventResult:
        try:
            event_payload = await self.events_repo.process_event(
                event_id, process_timeout=process_timeout
            )
        except EventProcessError as error:
            logger.error(f"event error:{error}")
            raise RuntimeError
        event_model = _get_model_for_event(event_type)
        return parse_obj_as(event_model, event_payload)  # type: ignore


def _get_model_for_event(
    event_type: EventTypes,
) -> Type["_EventResultType"]:
    return _EVENT_MAPPER[event_type]


_EventResultType = Union[
    DeviceDetail, DeviceHardware, List[InstalledProgram], Dict[str, str]
]
_EVENT_MAPPER = MappingProxyType(
    {
        EventTypes.detail: DeviceDetail,
        EventTypes.hardware: DeviceHardware,
        EventTypes.software: List[InstalledProgram],
        EventTypes.execute: dict,
        EventTypes.shutdown: dict,
    }
)
