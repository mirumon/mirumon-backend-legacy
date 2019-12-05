from typing import List

from fastapi import APIRouter, Depends

from app.models.schemas.computers import details
from app.services import event_handlers
from app.services.clients_manager import ClientsManager, get_clients_manager
from app.services.events_manager import EventsManager, get_events_manager

router = APIRouter()


@router.get("", response_model=List[details.ComputerInList], name="Devices List")
async def computers_list(
    clients_manager: ClientsManager = Depends(get_clients_manager),
    events_manager: EventsManager = Depends(get_events_manager),
) -> List[details.ComputerInList]:
    return await event_handlers.clients_list(clients_manager, events_manager)
