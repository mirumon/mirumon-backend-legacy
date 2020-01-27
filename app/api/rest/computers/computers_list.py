from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies.managers import (
    clients_manager_retriever,
    events_manager_retriever,
)
from app.models.schemas.computers import details
from app.services import event_handlers
from app.services.clients_manager import ClientsManager
from app.services.events_manager import EventsManager

router = APIRouter()


@router.get(
    "",
    name="events:list",
    response_model=List[details.ComputerOverview],
    summary="Devices List",
)
async def computers_list(
    clients_manager: ClientsManager = Depends(clients_manager_retriever()),
    events_manager: EventsManager = Depends(events_manager_retriever()),
) -> List[details.ComputerOverview]:
    return await event_handlers.get_devices_list(clients_manager, events_manager)
