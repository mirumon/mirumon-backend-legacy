from json import JSONDecodeError

from fastapi import APIRouter, Depends, Header
from loguru import logger
from pydantic import ValidationError
from starlette import status, websockets
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.dependencies.connections import get_clients_gateway_ws
from app.api.dependencies.services import get_devices_service_ws, get_events_service_ws
from app.services.devices.client import DeviceClient
from app.services.devices.devices_service import DevicesService
from app.services.devices.events_service import EventsService
from app.services.devices.gateway import DeviceClientsGateway

router = APIRouter()


async def get_registered_device_client(
    websocket: WebSocket,
    token: str = Header(None),
    devices_service: DevicesService = Depends(get_devices_service_ws),
    clients_manager: DeviceClientsGateway = Depends(get_clients_gateway_ws),
) -> DeviceClient:
    await websocket.accept()
    try:
        device = await devices_service.get_registered_device_by_token(token)
    except RuntimeError:
        logger.debug("device token decode error")
        await websocket.close(status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect
    else:
        client = DeviceClient(device_id=device.id, websocket=websocket)
        clients_manager.add_client(client)
        return client


@router.websocket("/service", name="devices:service")
async def device_ws_endpoint(
    client: DeviceClient = Depends(get_registered_device_client),
    events_service: EventsService = Depends(get_events_service_ws),
    clients_manager: DeviceClientsGateway = Depends(get_clients_gateway_ws),
) -> None:
    while client.is_connected:
        try:
            event = await client.read_event()
        except (ValidationError, JSONDecodeError) as validation_error:
            logger.debug("error {0}", validation_error)
            await client.send_error(validation_error, status.WS_1002_PROTOCOL_ERROR)
        except websockets.WebSocketDisconnect as disconnect_error:
            logger.info(
                "device:{0} disconnected, reason {1}",
                client.device_id,
                disconnect_error,
            )
            clients_manager.remove_client(client)
        else:
            logger.debug("received event from device")
            await events_service.send_event_response(event)
