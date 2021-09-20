import uuid

from mirumon.application.devices.commands.device_command import DeviceCommand


class SyncDeviceSystemCommand(DeviceCommand):
    sync_id: uuid.UUID
    device_id: uuid.UUID
    command_type: str = "sync_device_system"
    command_attributes: dict = {}  # type: ignore
