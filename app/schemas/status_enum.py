from enum import Enum


class StatusEnum(Enum):
    registration_success: str = "registration_success"
    registration_failed: str = "registration_failed"
    auth_success: str = "auth_success"
    auth_failed: str = "auth_failed"
