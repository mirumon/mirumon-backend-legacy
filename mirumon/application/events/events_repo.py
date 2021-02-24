from typing import Optional

from mirumon.application.events.models import EventID, EventInResponse, EventResult
from mirumon.application.repositories import Repository


class EventProcessError(Exception):
    """Error class for exit from consuming event."""


class EventsRepository(Repository):
    async def process_event(
        self, event_id: EventID, *, process_timeout: Optional[float] = None
    ) -> EventResult:
        raise NotImplementedError

    async def publish_event_response(self, event: EventInResponse) -> None:
        raise NotImplementedError
