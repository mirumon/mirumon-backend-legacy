from typing import Dict

from mirumon.domain.devices.entities import Device, DeviceID
from mirumon.infra.components.postgres.repo import PostgresRepository
from mirumon.infra.errors import EntityDoesNotExist
from mirumon.infra.infra_model import InfraModel


class DeviceInfraModel(InfraModel):
    id: DeviceID
    version: int = 1
    data: Dict[str, dict] = {}  # type: ignore

    @classmethod
    def from_entity(cls, device: Device) -> "DeviceInfraModel":  # type: ignore
        return cls.parse_obj(device.dict())


_storage: Dict[DeviceID, DeviceInfraModel] = {}


class DevicesRepository(PostgresRepository):
    """Fake storage implementation for devices."""

    async def create(self, device: Device) -> Device:
        infra_device = DeviceInfraModel.from_entity(device)
        _storage[infra_device.id] = infra_device
        return device

    async def get(self, device_id: DeviceID) -> Device:
        try:
            infra_device = _storage[device_id]
        except KeyError:
            raise EntityDoesNotExist()

        return infra_device.to_entity()
