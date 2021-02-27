from fastapi import APIRouter, Depends, Header
from loguru import logger
from starlette import status, websockets

from mirumon.application.devices.auth_service import DevicesAuthService
from mirumon.application.devices.events.system_info_synced import DeviceSystemInfoSynced
from mirumon.application.devices.gateway import DeviceClientsManager
from mirumon.application.devices.internal_protocol.models import DeviceAgentResponse
from mirumon.application.repositories import BrokerRepo
from mirumon.infra.api.dependencies.devices.connections import (
    get_device_clients_manager,
)
from mirumon.infra.api.dependencies.repositories import get_repository
from mirumon.infra.api.dependencies.services import get_service

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
    broker_repo: BrokerRepo = Depends(get_repository(BrokerRepo)),
    clients_manager: DeviceClientsManager = Depends(get_device_clients_manager),
) -> None:
    try:
        device = await auth_service.get_device_from_token(token)
    except RuntimeError as error:
        logger.debug(f"device token decode error:{error}")
        raise websockets.WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    await clients_manager.connect(device.id, websocket)

    while True:
        try:
            payload = await websocket.receive_text()
            response = DeviceAgentResponse.parse_raw(payload)
            if response.is_success:
                logger.debug(
                    "device:{} send successful response:{}", device.id, response.result
                )
                event = DeviceSystemInfoSynced(
                    sync_id=response.id, device_id=device.id, event_attributes=response.result
                )
                await broker_repo.publish_event(event)
            else:
                logger.debug(
                    "device:{} send unsuccessful response:{}", device.id, response.error
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
            break
