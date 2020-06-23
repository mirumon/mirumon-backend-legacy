from json import JSONDecodeError

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets
from starlette.websockets import WebSocket

from app.api.dependencies.services import get_devices_service
from app.domain.device.auth import DeviceCredentials
from app.domain.event.base import EventError
from app.services.devices.client import DeviceClient
from app.services.devices.devices_service import DevicesService

router = APIRouter()

WS_BAD_REQUEST_CODE = 400  # fixme change to correct code


async def get_registered_device_client(
    websocket: WebSocket, devices_service: DevicesService = Depends(get_devices_service)
) -> DeviceClient:
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        credentials = DeviceCredentials(**payload)
    except JSONDecodeError as decode_error:
        error = EventError(code=WS_BAD_REQUEST_CODE, detail=decode_error.msg)
        error_payload = {"error": error.dict()}
        await websocket.send_json(error_payload)
    except ValidationError as validation_error:
        error = EventError(code=WS_BAD_REQUEST_CODE, detail=validation_error.errors())
        error_payload = {"error": error.dict()}
        await websocket.send_json(error_payload)
    else:
        device = await devices_service.get_registered_device_by_token(credentials.token)
        client = DeviceClient(device_id=device.id, websocket=websocket)
        devices_service.add_client(client)
        return client


@router.websocket("/service", name="devices:service")
async def device_ws_endpoint(
    client: DeviceClient = Depends(get_registered_device_client),
    devices_service: DevicesService = Depends(get_devices_service),
) -> None:
    while client.is_connected:
        try:
            await devices_service.read_incoming_event(client)
        except RuntimeError as error:
            await devices_service.send_error(client, error, WS_BAD_REQUEST_CODE)
        except websockets.WebSocketDisconnect:
            logger.info("device:{0} disconnected", client.device_id)
            devices_service.remove_client(client)
