from mirumon.application.devices.device_socket_manager import (
    DevicesSocketManager,
    socket_manager,
)


def get_device_clients_manager() -> DevicesSocketManager:
    return socket_manager
