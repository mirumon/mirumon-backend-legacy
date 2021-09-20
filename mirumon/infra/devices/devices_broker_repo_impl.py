import json
import uuid

from aio_pika import Channel, Connection, ExchangeType, Message, Queue
from loguru import logger

from mirumon.application.devices.commands.device_command import DeviceCommand
from mirumon.application.devices.events.device_event import DeviceEvent
from mirumon.application.repo_protocol import Repository
from mirumon.domain.devices.entities import DeviceID


class DevicesBrokerRepoImpl(Repository):
    def __init__(self, connection: Connection, process_timeout: float) -> None:
        self.connection = connection
        self.process_timeout = process_timeout
        self.exchange: str = "mirumon.devices.topic"

    async def send_command(self, command: DeviceCommand) -> None:
        channel: Channel = await self.connection.channel()
        exchange = await channel.declare_exchange("devices")

        # TODO: move command_attributes to body and build keys by device_id
        headers = {
            "device_id": str(command.device_id),
            "command": command.command_type,
            "command_attributes": command.command_attributes,
        }
        body = command.json().encode()
        message = Message(
            body, headers=headers, correlation_id=command.sync_id, expiration=10
        )
        logger.debug(f"publish command to broker: {message}")
        await exchange.publish(message, routing_key="devices.commands")

    async def publish_event(self, event: DeviceEvent) -> None:
        channel: Channel = await self.connection.channel()
        exchange = await channel.declare_exchange(
            self.exchange, type=ExchangeType.TOPIC
        )

        headers = {
            "device_id": str(event.device_id),
            "event": event.event_type,
            "event_attributes": event.event_attributes_to_dict,
        }
        # TODO: move event_attributes to body and build keys by device_id
        body = event.json().encode()
        message = Message(body, headers=headers, correlation_id=str(event.sync_id))
        logger.debug(f"publish message to broker: {message}")
        key = f"devices.events.{event.event_type}"
        await exchange.publish(message, routing_key=key)

    async def consume(  # type: ignore
        self, device_id: DeviceID, sync_id: uuid.UUID, timeout_in_sec: int = 10
    ) -> dict:  # type: ignore
        channel: Channel = await self.connection.channel()
        queue: Queue = await channel.declare_queue("mirumon.devices.events")

        key = "devices.events.*"

        await queue.bind(self.exchange, routing_key=key)

        logger.debug(f"listen event with sync_id:{sync_id}")
        async with queue.iterator(timeout=timeout_in_sec) as queue_iter:
            async for message in queue_iter:
                if _skip_message(message, device_id, sync_id):
                    continue

                logger.debug(f"process message for device:{device_id}: {message}")
                logger.debug(f"message body: {message.body}")
                try:
                    payload = json.loads(message.body.decode())
                except json.decoder.JSONDecodeError as error:
                    logger.error(f"got error on message body decode:{error}")
                    raise RuntimeError("Message decode error")

                return payload


def _skip_message(message: Message, device_id: DeviceID, sync_id: uuid.UUID) -> bool:
    if str(message.correlation_id) != str(sync_id):
        logger.debug(f"correlation_id {message.correlation_id} != {sync_id}")
        return True

    header_id = message.headers.get("device_id")
    if str(header_id) != str(device_id):
        logger.debug(f"device_id {header_id} != {device_id}")
        return True

    return False
