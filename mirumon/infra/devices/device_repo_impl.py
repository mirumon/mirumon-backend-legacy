from typing import Dict

from mirumon.application.devices.devices_repo import DeviceDoesNotExist
from mirumon.domain.devices.entities import Device, DeviceID
from mirumon.infra.components.postgres.repo import PostgresRepository
from mirumon.infra.infra_model import InfraModel


class DeviceInfraModel(InfraModel):
    id: DeviceID
    name: str
    properties: Dict[str, dict] = {}  # type: ignore

    @classmethod
    def from_entity(cls, device: Device) -> "DeviceInfraModel":  # type: ignore
        return cls.parse_obj(device.dict())

    def to_entity(self) -> Device:  # type: ignore
        return Device(id=self.id, name=self.name, properties=self.properties)


_storage: Dict[DeviceID, DeviceInfraModel] = {}


class DevicesRepoImpl(PostgresRepository):
    """Fake storage implementation for devices."""

    # TODO: change to real tables
    async def create(self, device: Device) -> Device:
        infra_device = DeviceInfraModel.from_entity(device)
        _storage[infra_device.id] = infra_device
        return device

    async def get(self, device_id: DeviceID) -> Device:
        try:
            infra_device = _storage[device_id]
        except KeyError:
            raise DeviceDoesNotExist()

        return infra_device.to_entity()

    async def all(self) -> list[Device]:
        return [infra_device.to_entity() for _, infra_device in _storage.items()]
