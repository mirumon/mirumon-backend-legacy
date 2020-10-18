import uvicorn

from app.api.asgi import create_app
from app.settings.config import get_app_settings

settings = get_app_settings()
app = create_app(settings)

if __name__ == "__main__":
    uvicorn.run(app=app)
