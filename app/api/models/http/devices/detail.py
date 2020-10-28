from app.api.models.http.base import APIModel
from app.database.models.device import detail
from app.domain.devices.base import DeviceID


class DeviceDetail(APIModel, detail.DeviceInfo):
    id: DeviceID
    online: bool
