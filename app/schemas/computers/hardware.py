from typing import List, Optional

from pydantic import BaseModel


class MotherBoardModel(BaseModel):
    name: str
    caption: str
    status: str
    product: str
    serial_number: str


class ProcessorModel(BaseModel):
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


class VideoControllerModel(BaseModel):
    status: str
    name: str
    caption: str
    driver_version: str
    driver_date: str
    video_mode_description: str
    current_vertical_resolution: str


class NetworkAdapterModel(BaseModel):
    description: str
    mac_address: str
    ip_addresses: List[str]


class PhysicalDiskModel(BaseModel):
    status: str
    caption: str
    serial_number: Optional[str]
    size: float
    model: Optional[str]
    description: str
    partitions: int


class HardwareModel(BaseModel):
    mother: MotherBoardModel
    cpu: List[ProcessorModel]
    gpu: List[VideoControllerModel]
    network: List[NetworkAdapterModel]
    disks: List[PhysicalDiskModel]
