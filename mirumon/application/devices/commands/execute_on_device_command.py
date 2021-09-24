import uuid
from typing import Optional

from mirumon.application.devices.commands.device_command import DeviceCommand


class ExecuteOnDeviceCommand(DeviceCommand):
    command_id: uuid.UUID = uuid.uuid4()
    command_type: str = "execute_on_device"
    command_attributes: dict = {}  # type: ignore
    device_id: uuid.UUID
    correlation_id: Optional[uuid.UUID] = None
