import uuid

from starlette import websockets

from app.services.clients import Client


async def get_new_client(websocket: websockets.WebSocket,) -> Client:
    await websocket.accept()
    return Client(device_uid=uuid.uuid4(), websocket=websocket)
