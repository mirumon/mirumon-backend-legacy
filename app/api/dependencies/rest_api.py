from fastapi import Depends, HTTPException
from starlette import status

from app.api.dependencies.managers import ClientsManager, clients_manager_retriever
from app.models.schemas.events.rest import DeviceUID
from app.services import clients


def get_client(
    device_uid: DeviceUID,
    clients_manager: ClientsManager = Depends(clients_manager_retriever()),
) -> clients.Client:
    try:
        return clients_manager.get_client(device_uid)
    except KeyError as missed_websocket_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        ) from missed_websocket_error
