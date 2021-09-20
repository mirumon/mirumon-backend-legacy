from fastapi import APIRouter, Depends, Header
from loguru import logger
from starlette import status, websockets

from mirumon.api.dependencies.devices.connections import get_device_clients_manager
from mirumon.api.dependencies.repositories import get_repository
from mirumon.api.dependencies.services import get_service
from mirumon.application.devices.auth_service import DeviceInToken, DevicesAuthService
from mirumon.application.devices.device_broker_repo import DeviceBrokerRepo
from mirumon.application.devices.device_socket_manager import DevicesSocketManager
from mirumon.application.devices.device_socket_repo import DevicesSocketRepo
from mirumon.application.devices.events.device_event import DeviceEvent
from mirumon.application.devices.events.device_hardware_synced import (
    DeviceHardwareSynced,
)
from mirumon.application.devices.events.device_software_synced import (
    DeviceSoftwareSynced,
)
from mirumon.application.devices.events.device_system_synced import DeviceSystemSynced
from mirumon.application.devices.internal_api_protocol.models import DeviceAgentResponse

router = APIRouter()


def get_bearer_token(token: str = Header(..., alias="Authorization")) -> str:
    if token.startswith("Bearer "):
        return token.split(" ", 1)[1]
    return token


@router.websocket("/devices/connect/ws", name="devices:connect")
async def device_ws_endpoint(  # noqa: WPS231
    websocket: websockets.WebSocket,
    token: str = Depends(get_bearer_token),
    auth_service: DevicesAuthService = Depends(get_service(DevicesAuthService)),
    broker_repo: DeviceBrokerRepo = Depends(get_repository(DeviceBrokerRepo)),
    clients_manager: DevicesSocketManager = Depends(get_device_clients_manager),
    socket_repo: DevicesSocketRepo = Depends(get_repository(DevicesSocketRepo)),
) -> None:
    try:
        device = await auth_service.get_device_from_token(token)
    except RuntimeError as error:
        logger.debug(f"device token decode error:{error}")
        raise websockets.WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    await clients_manager.connect(device.id, websocket)
    await socket_repo.set_connected(device.id)

    while True:
        try:  # noqa: WPS229
            payload = await websocket.receive_text()
            logger.debug(f"received response from device:{device.id}\n{payload}")
            response = DeviceAgentResponse.parse_raw(payload)
        except ValueError as validation_error:
            logger.error(f"ws payload validation error {validation_error}")
        except websockets.WebSocketDisconnect as disconnect_error:
            logger.info(f"device:{device.id} disconnected, reason {disconnect_error}")
            await clients_manager.disconnect(device.id)
            await socket_repo.set_disconnected(device.id)
            break
        else:
            if response.is_success:
                await _publish_event(broker_repo, device, response)
            else:
                logger.error(
                    f"received error from device:{device.id}\n{response.error}"
                )


async def _publish_event(
    broker_repo: DeviceBrokerRepo, device: DeviceInToken, response: DeviceAgentResponse
) -> None:
    logger.debug(
        f"received successful result from device:{device.id}\n{response.result}",
    )
    try:
        event = _build_event(device, response)
    except KeyError:
        logger.error(
            f"received unknown method:{response.method} from device:{device.id}"
        )
    except Exception as unhandled_error:
        logger.exception(f"got error {unhandled_error}")
    else:
        await broker_repo.publish_event(event)


def _build_event(device: DeviceInToken, response: DeviceAgentResponse) -> DeviceEvent:
    method_to_event_mapper = {
        "sync_device_system": DeviceSystemSynced,
        "sync_device_hardware": DeviceHardwareSynced,
        "sync_device_software": DeviceSoftwareSynced,
    }
    model = method_to_event_mapper[response.method]
    return model(
        sync_id=response.id,
        device_id=device.id,
        event_attributes=response.result,
    )
