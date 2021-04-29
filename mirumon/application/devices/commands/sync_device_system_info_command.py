import uuid

from mirumon.application.devices.commands.device_command import DeviceCommand


class SyncDeviceSystemInfoCommand(DeviceCommand):
    sync_id: uuid.UUID
    device_id: uuid.UUID
    command_type: str = "sync_device_system_info"
    command_attributes: dict = {}  # type: ignore
