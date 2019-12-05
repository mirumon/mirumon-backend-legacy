from fastapi import Depends, HTTPException
from starlette import status

from app.models.schemas.events.rest import DeviceID
from app.services import clients
from app.services.clients_manager import ClientsManager, get_clients_manager


def get_client(
    device_id: DeviceID, clients_manager: ClientsManager = Depends(get_clients_manager)
) -> clients.Client:
    try:
        return clients_manager.get_client(device_id)
    except KeyError as missed_websocket_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        ) from missed_websocket_error
