import uuid

from mirumon.application.devices.commands.device_command import DeviceCommand
from mirumon.application.devices.events.device_event import DeviceEvent
from mirumon.application.repo_protocol import Repository
from mirumon.domain.devices.entities import DeviceID


class DeviceBrokerRepo(Repository):
    """Base broker repository class for typing and DI."""

    async def publish_event(self, event: DeviceEvent) -> None:
        raise NotImplementedError

    async def send_command(self, command: DeviceCommand) -> None:
        raise NotImplementedError

    async def get(
        self, device_id: DeviceID, message_id: uuid.UUID
    ) -> dict:  # type: ignore
        raise NotImplementedError
