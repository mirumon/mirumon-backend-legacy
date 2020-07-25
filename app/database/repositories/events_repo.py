import json

from aio_pika import DeliveryMode, Message
from loguru import logger

from app.domain.event.base import EventInResponse, SyncID
from app.settings.environments.base import AppSettings


class EventsRepository:
    def __init__(self, settings: AppSettings, queue, exchange) -> None:
        self.settings = settings
        self.queue = queue
        self.exchange = exchange

    async def publish_event_response(self, event: EventInResponse) -> None:
        body = event.json().encode()
        message = Message(body, delivery_mode=DeliveryMode.PERSISTENT)
        logger.debug(f"publish event response message")
        await self.exchange.publish(message, routing_key="info")

    async def process_event(self, event_id: SyncID) -> EventInResponse:
        logger.debug("start processing event:{0}...", event_id)
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                logger.debug("message {0}", message)
                async with message.process():
                    logger.debug(f"process message: {message.body}")
                    body = message.body.decode()
                    d = json.loads(body)
                    event = EventInResponse(**d)
                    if event.sync_id == event_id:
                        return event
