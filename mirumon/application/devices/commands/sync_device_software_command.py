import uuid
from typing import Optional

from mirumon.application.devices.commands.device_command import DeviceCommand


class SyncDeviceSoftwareCommand(DeviceCommand):
    command_id: uuid.UUID = uuid.uuid4()
    command_type: str = "sync_device_software"
    command_attributes: dict = {}  # type: ignore
    device_id: uuid.UUID
    correlation_id: Optional[uuid.UUID] = None
