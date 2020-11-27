"""Text for documentation and API messages"""

# Views description for swagger
DEVICES_CREATE_DESCRIPTION = (
    "Register a device for server. Return a token for usage in device connection."
)
DEVICES_LIST_DESCRIPTION = "List of all available devices"
DEVICES_DETAIL_DESCRIPTION = "Detail information about device"
DEVICES_HARDWARE_DESCRIPTION = "Hardware information of device"
DEVICES_SOFTWARE_DESCRIPTION = "Installed programs on device"
DEVICES_EXECUTE_DESCRIPTION = "Background runs a command on the device"

DEVICES_SHUTDOWN_DESCRIPTION = (
    "Shutdown device. "
    "Does not disconnect the device from the server "  # noqa: WPS326
    "until the device itself turns off"  # noqa: WPS326
)


# Users API messages
USER_DOES_NOT_EXIST_ERROR = "user does not exist"

INCORRECT_LOGIN_INPUT = "incorrect login or password or scopes"
USERNAME_TAKEN = "user with this username already exists"

WRONG_TOKEN_PREFIX = "unsupported authorization type"  # noqa: S105
MALFORMED_PAYLOAD = "could not validate credentials"

NOT_ENOUGH_PRIVILEGES = "unable to perform action"

# Devices API messages
INVALID_SHARED_KEY = "invalid shared key"
EVENT_NOT_SUPPORTED = "event is not supported by device"
DEVICE_DISCONNECTED = "device disconnected"
DEVICE_NOT_FOUND = "The device was not found"
