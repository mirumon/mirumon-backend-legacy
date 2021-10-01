import asyncio
import json
import uuid

import aio_pika
from loguru import logger

from mirumon.application.devices.commands.device_command import DeviceCommand
from mirumon.application.devices.events.device_event import DeviceEvent
from mirumon.application.repo_protocol import Repository
from mirumon.domain.devices.entities import DeviceID


class DevicesBrokerRepoImpl(Repository):
    _channel: aio_pika.Channel
    _commands_exchange: aio_pika.Exchange
    _events_exchange: aio_pika.Exchange
    _events_queue: aio_pika.Queue

    def __init__(
        self,
        connection: aio_pika.Connection,
        process_timeout: float = 5,
        expiration: float = 15,
    ) -> None:
        self.connection = connection
        self.process_timeout = process_timeout
        self.expiration = expiration

    async def start(self) -> None:
        logger.debug(f"{self.__class__} start() called")
        self._channel: aio_pika.Channel = await self.connection.channel()

        self._commands_exchange = await self._channel.declare_exchange(
            "mirumon.devices.commands", type="topic", auto_delete=False, durable=True
        )
        self._events_exchange = await self._channel.declare_exchange(
            "mirumon.devices.events", type="topic", auto_delete=False, durable=True
        )
        self._events_queue: aio_pika.Queue = await self._channel.declare_queue(
            "devices.events.queue"
        )
        await self._events_queue.bind(
            self._events_exchange, routing_key="devices.*.events.*"
        )

    async def close(self) -> None:
        await self._channel.close()  # type: ignore

    async def send_command(self, command: DeviceCommand) -> None:
        key = _build_command_routing_key(command)
        body = json.dumps(command.command_attributes).encode()
        headers = {
            "device_id": str(command.device_id),
            "command_type": str(command.command_type),
        }
        message = aio_pika.Message(
            body,
            message_id=str(command.command_id),
            type="application/json",
            headers=headers,
            correlation_id=command.correlation_id,
            expiration=self.expiration,
        )

        logger.debug(f"publish command to broker: {command}")
        await self._commands_exchange.publish(message, routing_key=key)

    async def publish_event(self, event: DeviceEvent) -> None:
        key = _build_event_routing_key(event)
        headers = {
            "device_id": str(event.device_id),
            "event_type": str(event.event_type),
        }
        body = event.json().encode()
        message = aio_pika.Message(
            body,
            message_id=str(event.event_id),
            headers=headers,
            correlation_id=str(event.correlation_id),
            expiration=self.expiration,
        )

        logger.debug(f"publish event to broker: {event}")
        await self._events_exchange.publish(message, routing_key=key)

    async def get(
        self, device_id: DeviceID, correlation_id: uuid.UUID, timeout_in_sec: int = 10
    ) -> dict:  # type: ignore
        logger.debug(
            f"trying to get event by device_id:{device_id}, correlation_id:{correlation_id}"  # noqa: E501
        )
        try:
            return await self._get(device_id, correlation_id, timeout_in_sec)
        except asyncio.exceptions.TimeoutError as error:
            raise RuntimeError("Consume timeout") from error

    async def _get(  # type: ignore
        self, device_id: DeviceID, correlation_id: uuid.UUID, timeout_in_sec: int
    ) -> dict:  # type: ignore
        async with self._events_queue.iterator(timeout=timeout_in_sec) as queue_iter:
            async for message in queue_iter:
                logger.debug(f"iter message with message_id:{message.message_id}")
                if _skip_message(message, device_id, correlation_id):
                    continue

                body = message.body
                try:
                    payload = json.loads(body.decode())
                except json.decoder.JSONDecodeError as error:
                    message.nack()
                    raise RuntimeError("Message body decode error") from error
                message.ack()

                return payload


def _build_command_routing_key(command: DeviceCommand) -> str:
    return f"devices.{command.device_id}.commands.{command.command_id}"


def _build_event_routing_key(event: DeviceEvent) -> str:
    return f"devices.{event.device_id}.events.{event.event_id}"


def _skip_message(
    message: aio_pika.Message, device_id: DeviceID, correlation_id: uuid.UUID
) -> bool:
    if str(message.correlation_id) != str(correlation_id):
        logger.debug(f"skip event with correlation_id {message.correlation_id}")
        return True

    message_device_id = message.headers.get("device_id")
    if str(message_device_id) != str(device_id):
        logger.debug(f"skip event with device_id {message_device_id}")
        return True

    return False
