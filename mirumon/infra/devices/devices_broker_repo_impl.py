import json

from aio_pika import Channel, Connection, Message, Queue, ExchangeType
from loguru import logger

from mirumon.application.repo_protocol import Repository


class DeviceBrokerRepoImpl(Repository):
    def __init__(self, connection: Connection, process_timeout: float) -> None:
        self.connection = connection
        self.process_timeout = process_timeout
        self.exchange = "mirumon.devices.topic"

    async def send_command(self, command) -> None:
        channel: Channel = await self.connection.channel()
        exchange = await channel.declare_exchange("devices")

        headers = {
            "device_id": str(command.device_id),
            "command": command.command_type,
            "command_attributes": command.command_attributes,
        }
        body = command.json().encode()
        message = Message(body, headers=headers, correlation_id=command.sync_id)
        logger.debug(f"publish command to broker: {message}")
        await exchange.publish(message, routing_key=f"devices.commands")

    async def publish_event(self, event) -> None:
        channel: Channel = await self.connection.channel()
        exchange = await channel.declare_exchange(self.exchange, type=ExchangeType.TOPIC)

        headers = {
            "device_id": str(event.device_id),
            "event": event.event_type,
            "event_attributes": event.event_attributes_to_dict,
        }
        # todo: move attrs to body
        body = event.json().encode()
        message = Message(body, headers=headers, correlation_id=str(event.sync_id))
        logger.debug("publish event to broker: {}", message)
        key = f"devices.events.{event.event_type}"
        print(f"publish event key: {key}")
        await exchange.publish(message, routing_key=key)

    async def consume(self, device_id, sync_id, timeout_in_sec: int = 10):
        channel: Channel = await self.connection.channel()
        queue: Queue = await channel.declare_queue("mirumon.devices.events")

        key = f"devices.events.*"
        print(f"consume event key: {key}")

        await queue.bind(self.exchange, routing_key=key)

        logger.debug("listen event with sync_id:{0}", sync_id)
        async with queue.iterator(timeout=timeout_in_sec) as queue_iter:
            async for message in queue_iter:
                logger.critical(f"message: corr_id: {message.correlation_id}, device_id: {message.headers.get('device_id')}")
                if str(message.correlation_id) != str(sync_id):
                    logger.debug(f"correlation_id {message.correlation_id} != {sync_id}")
                    continue
                if str(message.headers.get("device_id")) != str(device_id):
                    logger.debug(f"device_id {message.headers.get('device_id')} != {device_id}")
                    continue

                logger.debug("process message for device:{0}: {0}", device_id, message)
                logger.debug("raw message: {}", message.body)
                try:
                    payload = json.loads(message.body.decode())
                    print(payload)
                except Exception as e:
                    logger.debug("got error on message body decode:{}", e)
                    raise RuntimeError("Message decode error")

                print("ACKED")

                return payload

    async def bulk_consume(self, timeout_in_sec: int = 10):
        channel: Channel = await self.connection.channel()
        queue: Queue = await channel.declare_queue("mirumon.devices.events")
        key = f"devices.events.*"
        await queue.bind(self.exchange, routing_key=key)

        async with queue.iterator(timeout=timeout_in_sec) as queue_iter:
            async for message in queue_iter:
                logger.critical(
                    f"bulk_message: corr_id: {message.correlation_id}, device_id: {message.headers.get('device_id')}")

                logger.debug("process message: {}", message)
                logger.debug("raw message: {}", message.body)
                try:
                    payload = json.loads(message.body.decode())
                except Exception as e:
                    logger.error("got error on message body decode:{}", e)
                    continue
                print("BULK_ACKED")

                yield payload
