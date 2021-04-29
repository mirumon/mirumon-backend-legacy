from mirumon.application.devices.device_socket_manager import DeviceSocketManager, socket_manager


def get_device_clients_manager() -> DeviceSocketManager:
    return socket_manager
