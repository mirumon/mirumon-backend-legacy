from typing import Optional

from mirumon.api.api_model import APIModel


class MotherBoard(APIModel):
    name: str
    caption: str
    status: str
    product: str
    serial_number: str


class Processor(APIModel):
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


class VideoController(APIModel):
    status: str
    name: str
    caption: str
    driver_version: str
    driver_date: str
    video_mode_description: str
    current_vertical_resolution: str


class NetworkAdapter(APIModel):
    description: str
    mac_address: str
    ip_addresses: list[str]


class PhysicalDisk(APIModel):
    status: str
    caption: str
    serial_number: Optional[str]
    size: float
    model: Optional[str]
    description: str
    partitions: int


class GetDeviceHardwareResponse(APIModel):
    motherboard: MotherBoard
    cpu: list[Processor]
    gpu: list[VideoController]
    network: list[NetworkAdapter]
    disks: list[PhysicalDisk]
