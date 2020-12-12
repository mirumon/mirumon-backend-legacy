from fastapi import APIRouter

from mirumon.infra.api.devices import devices_router
from mirumon.infra.api.users import users_router

router = APIRouter()


router.include_router(users_router.router)
router.include_router(devices_router.router)
