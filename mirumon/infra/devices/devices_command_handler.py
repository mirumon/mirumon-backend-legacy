import asyncio
import json
from typing import Optional

from aio_pika import Channel, Connection, ExchangeType, IncomingMessage
from loguru import logger
from pydantic import parse_obj_as
from starlette.websockets import WebSocket

from mirumon.application.devices.device_socket_manager import DevicesSocketManager
from mirumon.application.devices.internal_api_protocol.models import DeviceAgentRequest
from mirumon.domain.devices.entities import DeviceID

# Example https://github.com/STUDITEMPS/aio-restrabbit/blob/master/aiorestrabbit/client.py  # noqa: E501


class DeviceCommandHandler:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        broker_connection: Connection,
        socket_manager: DevicesSocketManager,
    ) -> None:
        self.loop = loop
        self.connection = broker_connection
        self.socket_manager = socket_manager

    async def start(self) -> None:
        channel: Channel = await self.connection.channel()

        exchange = await channel.declare_exchange("devices", ExchangeType.DIRECT)

        # Declare a queue and disable saving messages,
        # since messages have a small life cycle and we can save memory
        queue = await channel.declare_queue("devices_commands", auto_delete=True)
        await queue.bind(exchange, routing_key="devices.commands")
        self.task = self.loop.create_task(queue.consume(self.handle))

    async def handle(self, message: IncomingMessage) -> None:
        logger.debug(f"handle message:{message}")
        id = message.headers["device_id"]
        device_id = parse_obj_as(DeviceID, id)
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
            method = payload["command_type"]
            params = payload["command_attributes"]
            payload_json = DeviceAgentRequest(
                id=message.correlation_id, method=method, params=params
            ).json()
            logger.debug(f"send request to agent {repr(payload_json)}")  # noqa: WPS237
            await device_client.send_text(payload_json)
        else:
            logger.debug(f"device:{device_id} not found in {self.socket_manager}")
