import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.dependencies.managers import (
    clients_manager_retriever,
    events_manager_retriever,
)
from app.common import config
from app.models.schemas.computers import details
from app.models.schemas.events.rest import RegistrationInRequest, RegistrationInResponse
from app.services import event_handlers
from app.services.clients_manager import ClientsManager
from app.services.events_manager import EventsManager

router = APIRouter()


@router.get("", name="events:registration", summary="Device Registration")
async def register_computer(
    registration_data: RegistrationInRequest,
) -> RegistrationInResponse:
    if registration_data.shared_token != config.SHARED_TOKEN:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="invalid shared token"
        )
    # TODO token generation, saving into db
    return RegistrationInResponse(device_token=str(uuid.uuid4()))


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
