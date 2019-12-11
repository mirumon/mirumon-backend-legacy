from starlette import websockets


async def get_accepted_websocket(
    websocket: websockets.WebSocket,
) -> websockets.WebSocket:
    await websocket.accept()
    return websocket
