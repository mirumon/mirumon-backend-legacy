from typing import List, Optional

from mirumon.domain.core.event import DomainEvent, frozen_dataclass


@frozen_dataclass
class MotherBoardModel:
    name: str
    caption: str
    status: str
    product: str
    serial_number: str


@frozen_dataclass
class ProcessorModel:
    status: str
    name: str
    caption: str
    current_clock_speed: str
    current_cthread_countlock_speed: Optional[int]
    virtualization_firmware_enabled: bool
    load_percentage: int
    number_of_cores: int
    number_of_enabled_core: int
    number_of_logical_processors: int


@frozen_dataclass
class VideoControllerModel:
    status: str
    name: str
    caption: str
    driver_version: str
    driver_date: str
    video_mode_description: str
    current_vertical_resolution: str


@frozen_dataclass
class NetworkAdapterModel:
    description: str
    mac_address: str
    ip_addresses: List[str]


@frozen_dataclass
class PhysicalDiskModel:
    status: str
    caption: str
    serial_number: Optional[str]
    size: float
    model: Optional[str]
    description: str
    partitions: int


@frozen_dataclass
class DeviceHardware(DomainEvent):
    motherboard: MotherBoardModel
    cpu: List[ProcessorModel]
    gpu: List[VideoControllerModel]
    network: List[NetworkAdapterModel]
    disks: List[PhysicalDiskModel]
