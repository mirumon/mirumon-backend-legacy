from json import JSONDecodeError

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import ValidationError
from starlette import websockets

from app.services.computers import (
    ClientsManager,
    client_registration,
    get_clients_manager,
)
from app.services.events import (
    EventsManager,
    get_events_manager,
    process_incoming_event,
)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: websockets.WebSocket,
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> None:
    await websocket.accept()
    try:
        client = await client_registration(websocket)
    except websockets.WebSocketDisconnect:
        return logger.info(f"registration failed")
    clients_manager.add_client(client)

    while True:
        try:
            await process_incoming_event(client, events_manager)
        except websockets.WebSocketDisconnect:
            logger.info(f"ws closed {client.mac_address}")
        except (JSONDecodeError, ValidationError):
            logger.warning("validation error")
            client.close()
        finally:
            clients_manager.remove_client(client)
            break
