import uvicorn

from mirumon.infra.api.asgi import create_app
from mirumon.settings.config import get_app_settings

settings = get_app_settings()
app = create_app(settings)

if __name__ == "__main__":
    uvicorn.run(app=app)
