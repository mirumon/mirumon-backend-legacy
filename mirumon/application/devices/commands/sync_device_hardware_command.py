import uuid

from mirumon.application.devices.commands.device_command import DeviceCommand


class SyncDeviceHardwareCommand(DeviceCommand):
    sync_id: uuid.UUID
    device_id: uuid.UUID
    command_type: str = "sync_device_hardware"
    command_attributes: dict = {}  # type: ignore
