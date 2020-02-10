import uuid

from starlette import websockets

from app.services.clients import DeviceClient


async def get_new_client(websocket: websockets.WebSocket,) -> DeviceClient:
    await websocket.accept()
    # TODO: check device token
    return DeviceClient(device_uid=uuid.uuid4(), websocket=websocket)
