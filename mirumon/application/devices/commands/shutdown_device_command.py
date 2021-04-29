import uuid

from mirumon.application.devices.commands.device_command import DeviceCommand


class ShutdownDeviceCommand(DeviceCommand):
    sync_id: uuid.UUID
    device_id: uuid.UUID
    command_type: str = "shutdown_device"
    command_attributes: dict = {}  # type: ignore
