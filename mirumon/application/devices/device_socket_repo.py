from mirumon.application.repo_protocol import Repository
from mirumon.domain.devices.entities import DeviceID


class DevicesSocketRepo(Repository):
    async def set_connected(self, device_id: DeviceID) -> bool:
        raise NotImplementedError

    async def set_disconnected(self, device_id: DeviceID) -> bool:
        raise NotImplementedError

    async def is_connected(self, device_id: DeviceID) -> bool:
        raise NotImplementedError
