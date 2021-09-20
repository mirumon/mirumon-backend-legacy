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


def get_token(token: str = Header(..., alias="Authorization")) -> str:
    if token.startswith("Bearer "):
        return token.split(" ", 1)[1]
    return token


@router.websocket("/devices/service", name="devices:service")
async def device_ws_endpoint(  # noqa: WPS231
    websocket: websockets.WebSocket,
    token: str = Depends(get_token),
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
        try:
            payload = await websocket.receive_text()
            logger.debug("received response from device:{}\n{}", device.id, payload)
            response = DeviceAgentResponse.parse_raw(payload)
            if response.is_success:
                logger.debug(
                    "received successful result from device:{}\n{}",
                    device.id,
                    response.result,
                )
                try:
                    event = _build_event(device, response)
                    await broker_repo.publish_event(event)
                except KeyError:
                    logger.error(
                        "received unknown method:{} from device:{}",
                        response.method,
                        device.id,
                    )
                except Exception as e:
                    logger.exception("got error {}", e)
            else:
                logger.error(
                    "received error from device:{}\n{}", device.id, response.error
                )
        except ValueError as validation_error:
            logger.debug("error {0}", validation_error)
        except websockets.WebSocketDisconnect as disconnect_error:
            logger.info(
                "device:{0} disconnected, reason {1}",
                device.id,
                disconnect_error,
            )
            await clients_manager.disconnect(device.id)
            await socket_repo.set_disconnected(device.id)
            break


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
