from mirumon.application.devices.gateway import DeviceClientsManager, conn_manager


def get_device_clients_manager() -> DeviceClientsManager:
    return conn_manager
