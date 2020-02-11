from starlette import websockets

from app.services.authentication import get_device_uid_by_token
from app.services.clients import DeviceClient


async def get_device_client(websocket: websockets.WebSocket) -> DeviceClient:
    await websocket.accept()
    # TODO: create models for payloads
    payload = await websocket.receive_json()
    device_token = payload["device_token"]
    device_uid = await get_device_uid_by_token(device_token)

    await websocket.send_json({"device_uid": str(device_uid)})
    return DeviceClient(device_uid=device_uid, websocket=websocket)
