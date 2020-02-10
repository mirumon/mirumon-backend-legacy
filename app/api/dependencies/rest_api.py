from fastapi import Depends, HTTPException
from starlette import status

from app.api.dependencies.managers import (
    ClientsManager,
    clients_manager_retriever,
    events_manager_retriever,
)
from app.models.domain.types import DeviceUID, SyncID
from app.services import clients
from app.services.events_manager import EventsManager


def get_client(
    device_uid: DeviceUID,
    clients_manager: ClientsManager = Depends(clients_manager_retriever()),
) -> clients.DeviceClient:
    try:
        return clients_manager.get_client(device_uid)
    except KeyError as missed_websocket_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="device not found"
        ) from missed_websocket_error


def get_new_sync_id(
    events_manager: EventsManager = Depends(events_manager_retriever()),
) -> SyncID:
    return events_manager.register_event()
