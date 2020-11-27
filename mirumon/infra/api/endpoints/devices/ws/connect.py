from fastapi import APIRouter, Depends, Header
from loguru import logger
from pydantic import ValidationError
from starlette import status, websockets
from starlette.websockets import WebSocket, WebSocketDisconnect

from mirumon.application.devices.auth_service import DevicesAuthService
from mirumon.application.devices.events_service import EventsService
from mirumon.application.devices.gateway import DeviceClientsManager
from mirumon.infra.api.dependencies.devices.connections import (
    get_device_clients_manager,
)
from mirumon.infra.api.dependencies.services import get_service

router = APIRouter()


def get_token(token: str = Header(..., alias="Authorization")) -> str:
    if token.startswith("Bearer "):
        return token.split(" ", 1)[1]
    return token


@router.websocket("/service", name="devices:service")
async def device_ws_endpoint(  # noqa: WPS231
    websocket: WebSocket,
    token: str = Depends(get_token),
    auth_service: DevicesAuthService = Depends(get_service(DevicesAuthService)),
    events_service: EventsService = Depends(get_service(EventsService)),
    clients_manager: DeviceClientsManager = Depends(get_device_clients_manager),
) -> None:
    try:
        device = await auth_service.get_device_from_token(token)
    except RuntimeError as error:
        logger.debug(f"device token decode error:{error}")
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    client = await clients_manager.connect(device.id, websocket)

    while True:
        try:
            event = await client.read_event()
        except ValidationError as validation_error:
            logger.debug("error {0}", validation_error.errors())
            await client.send_errors(validation_error.errors())
        except websockets.WebSocketDisconnect as disconnect_error:
            logger.info(
                "device:{0} disconnected, reason {1}",
                client.device_id,
                disconnect_error,
            )
            await clients_manager.disconnect(client.device_id)
            break
        else:
            logger.debug("received event from device")
            await events_service.send_event_response(event)
