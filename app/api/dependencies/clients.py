from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from starlette import status, websockets

from app.api.dependencies.managers import clients_manager_retriever
from app.api.dependencies.websockets import get_accepted_websocket
from app.services.clients import Client
from app.services.clients_manager import ClientsManager
from app.services.event_handlers import client_registration


async def process_registered_client(
    websocket: websockets.WebSocket = Depends(get_accepted_websocket),
    manager: ClientsManager = Depends(clients_manager_retriever(for_websocket=True)),
) -> AsyncGenerator[Client, None]:
    try:
        client = await client_registration(websocket)
    except websockets.WebSocketDisconnect:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="failed to register client"
        )

    manager.add_client(client)
    yield client
    manager.remove_client(client)
