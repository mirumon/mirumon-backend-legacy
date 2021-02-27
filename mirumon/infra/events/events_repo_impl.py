import json
from asyncio import exceptions
from typing import Optional, cast

from aio_pika import Channel, Connection, Exchange, Message, Queue
from aio_pika.queue import QueueIterator
from async_timeout import timeout
from loguru import logger
from pydantic import ValidationError

from mirumon.application.events.events_repo import EventProcessError
from mirumon.application.events.models import EventID, EventInResponse, EventResult
from mirumon.application.repositories import Repository


class BrokerRepoImpl(Repository):
    def __init__(self, connection: Connection, process_timeout: float) -> None:
        self.connection = connection
        self.process_timeout = process_timeout

    async def publish_command(self, command) -> None:
        channel: Channel = await self.connection.channel()
        exchange = await channel.declare_exchange("devices")

        for device_id in command.device_ids:
            headers = {
                "device_id": str(device_id),
                "command": command.command_type,
                "command_attributes": command.command_attributes,
            }
            body = command.json().encode()
            message = Message(body, headers=headers, correlation_id=command.sync_id)
            logger.debug(f"publish command to broker: {message}")
            await exchange.publish(message, routing_key="devices.commands")

    async def publish_event(self, event) -> None:
        print(event)
        channel: Channel = await self.connection.channel()
        exchange = await channel.declare_exchange("devices")

        headers = {
            "device_id": str(event.device_id),
            "command": event.event_type,
            "command_attributes": event.event_attributes,
        }
        body = event.json().encode()
        message = Message(body, headers=headers, correlation_id=event.sync_id)
        logger.debug(f"publish event to broker: {message}")
        await exchange.publish(message, routing_key="devices.events")

    async def consume(self, sync_id):
        channel: Channel = await self.connection.channel()
        queue: Queue = await channel.declare_queue("devices_events")
        await queue.bind("devices", routing_key="devices.events")

        logger.debug("listen event with sync_id:{0}", sync_id)
        # async with timeout(timeout=5):
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logger.debug("process message: {0}", message)
                if message.correlation_id == str(sync_id):
                    payload = json.loads(message.body.decode())
                    logger.debug("raw message: {}", message.body)
                    return payload


class EventsRepositoryImplementation(Repository):
    def __init__(
        self, queue: Queue, exchange: Exchange, process_timeout: float
    ) -> None:
        self.queue: Queue = queue
        self.exchange: Exchange = exchange
        self.process_timeout = process_timeout

    # old
    async def publish_event_response(self, event: EventInResponse) -> None:
        body = event.json().encode()
        message = Message(body)
        logger.debug(f"publish event response message:{message}")
        # await self.exchange.publish(message, routing_key="info")

    async def process_event(
        self, event_id: EventID, *, process_timeout: Optional[float] = None
    ) -> EventResult:
        logger.debug("start processing event:{0}", event_id)
        process_timeout = process_timeout or self.process_timeout
        try:
            async with timeout(timeout=process_timeout):
                return await self._wait_event(event_id)
        except exceptions.TimeoutError:
            logger.debug(f"timeout error on event:{event_id}")
            raise EventProcessError
        except RuntimeError:
            logger.warning(f"response with error from device on event:{event_id}")
            raise EventProcessError

    async def _wait_event(self, event_id: EventID) -> EventResult:
        async with self.queue.iterator() as queue_iter:
            return None
            # return await _process_message(queue_iter, event_id)


async def _process_message(  # noqa: WPS231
    queue_iter: QueueIterator, event_id: EventID
) -> EventResult:
    async for message in queue_iter:
        async with message.process():
            try:
                event = _validate_incoming_event(message)
            except ValidationError as error:
                logger.error(f"event message validation error:{error.errors()}")
                continue

            if event.id != event_id:
                continue

            if event.is_success:
                return cast(EventResult, event.result)
            raise RuntimeError("event contains error")

    raise RuntimeError("undefined error in message queue")


def _validate_incoming_event(message: Message) -> EventInResponse:
    raw_payload = message.body.decode()
    logger.debug(f"process message: {raw_payload}")
    return EventInResponse.parse_raw(raw_payload)
