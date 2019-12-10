from app.db.repositories.base import BaseRepository
from app.models.domain.devices import Device

CREATE_DEVICE_QUERY = """
INSERT INTO devices (name, mac_addr, data)
VALUES ($1, $2, $3)
ON CONFLICT DO NOTHING
RETURNING id
"""
ADD_DEVICE_TO_GLOBAL_GROUP = """
INSERT INTO devices_to_groups (device_id, group_id) 
SELECT $1, id
FROM device_groups
ON CONFLICT DO NOTHING 
"""


class DevicesRepository(BaseRepository):
    async def register_new_device(self, *, device: Device) -> None:
        device_id = await self._log_and_fetch_value(
            CREATE_DEVICE_QUERY, device.name, device.mac_addr, device.data
        )
        await self._log_and_execute(ADD_DEVICE_TO_GLOBAL_GROUP, device_id)

