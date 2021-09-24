import asyncio
import json
from typing import Optional

import aio_pika
import pydantic
from loguru import logger
from starlette.websockets import WebSocket

from mirumon.application.devices.device_socket_manager import DevicesSocketManager
from mirumon.application.devices.internal_api_protocol.models import DeviceAgentRequest
from mirumon.domain.devices.entities import DeviceID

# Example https://github.com/STUDITEMPS/aio-restrabbit/blob/master/aiorestrabbit/client.py  # noqa: E501


class DeviceCommandHandler:
    _channel: aio_pika.Channel
    connection: aio_pika.Connection

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        broker_connection: aio_pika.Connection,
        socket_manager: DevicesSocketManager,
    ) -> None:
        self.loop = loop
        self.connection = broker_connection
        self.socket_manager = socket_manager

    async def start(self) -> None:
        logger.debug(f"{self.__class__} start() called")
        channel: aio_pika.Channel = await self.connection.channel()

        # should same as exchange and queue in broker repo
        commands_exchange = await channel.declare_exchange(
            "mirumon.devices.commands", type="topic", auto_delete=False, durable=True
        )
        commands_queue: aio_pika.Queue = await channel.declare_queue(
            "devices.commands.queue"
        )
        await commands_queue.bind(commands_exchange, routing_key="devices.*.commands.*")

        self.task = self.loop.create_task(commands_queue.consume(self.handle))

    async def close(self) -> None:
        await self._channel.close()  # type: ignore

    @logger.catch
    async def handle(self, message: aio_pika.IncomingMessage) -> None:
        logger.debug(f"handle message:{message}")
        id = message.headers["device_id"]
        device_id = pydantic.parse_obj_as(DeviceID, id)
        logger.debug(f"device_id in command {device_id}")
        logger.debug(f"devices conns {self.socket_manager}")

        try:
            device_client: Optional[WebSocket] = self.socket_manager.get_client(
                device_id
            )
        except KeyError:
            logger.debug(f"can not send event to unconnected device:{device_id}")
            return

        logger.debug(f"device client {device_client}")
        if device_client:
            payload = json.loads(message.body.decode())
            method = message.headers.get("command_type")
            payload_json = DeviceAgentRequest(
                correlation_id=message.correlation_id, method=method, params=payload
            ).json()
            logger.debug(f"send request to agent {repr(payload_json)}")  # noqa: WPS237
            await device_client.send_text(payload_json)
        else:
            logger.debug(f"device:{device_id} not found in {self.socket_manager}")
