class DevicesRepository:
    def __init__(self):
        self._tokens = {}

    def get_device_by_token(self, token):
        for device_id, device_token in self._tokens.items():
            if device_token == token:
                return device_id
        raise KeyError("device with that token not found")
