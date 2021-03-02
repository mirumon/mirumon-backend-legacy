import json

from aio_pika import Channel, Connection, Message, Queue
from async_timeout import timeout
from loguru import logger

from mirumon.application.repositories import Repository


class DeviceBrokerRepoImpl(Repository):
    def __init__(self, connection: Connection, process_timeout: float) -> None:
        self.connection = connection
        self.process_timeout = process_timeout

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
        await exchange.publish(message, routing_key="devices.commands")

    async def publish_event(self, event) -> None:
        channel: Channel = await self.connection.channel()
        exchange = await channel.declare_exchange("devices")

        headers = {
            "device_id": str(event.device_id),
            "event": event.event_type,
            "event_attributes": event.event_attributes_to_dict,
        }
        body = event.json().encode()
        message = Message(body, headers=headers, correlation_id=event.sync_id)
        logger.debug("publish event to broker: {}", message)
        await exchange.publish(message, routing_key="devices.events")

    async def consume(self, sync_id):
        channel: Channel = await self.connection.channel()
        queue: Queue = await channel.declare_queue("devices_events")
        await queue.bind("devices", routing_key="devices.events")

        logger.debug("listen event with sync_id:{0}", sync_id)
        async with timeout(timeout=4):
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    logger.debug("process message: {0}", message)
                    logger.debug("raw message: {}", message.body)
                    if message.correlation_id == str(sync_id):
                        logger.debug(
                            "sync_id matched with correlation_id:{}",
                            message.correlation_id,
                        )
                        try:
                            payload = json.loads(message.body.decode())
                        except Exception as e:
                            logger.debug("got error on message body decode:{}", e)
                        return payload
                    else:
                        logger.debug(
                            "sync_id:{} didnt match with correlation_id:{}",
                            str(sync_id),
                            message.correlation_id,
                        )
