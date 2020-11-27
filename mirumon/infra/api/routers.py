from fastapi import APIRouter

from mirumon.infra.api.endpoints.devices.router import router as devices_router
from mirumon.infra.api.endpoints.users.router import router as users_router

router = APIRouter()


router.include_router(users_router)
router.include_router(devices_router)
