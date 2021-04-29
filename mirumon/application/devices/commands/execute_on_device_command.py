import uuid

from mirumon.application.devices.commands.device_command import DeviceCommand


class ExecuteOnDeviceCommand(DeviceCommand):
    sync_id: uuid.UUID
    device_id: uuid.UUID
    command_type: str = "execute_on_device"
    command_attributes: dict = {}  # type: ignore
