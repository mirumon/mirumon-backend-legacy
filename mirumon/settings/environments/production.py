from mirumon.settings.environments.app import AppSettings


class ProdAppSettings(AppSettings):
    """Application settings with override params for production environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = False

    # Custom settings
    disable_docs: bool = False

    class Config(AppSettings.Config):
        env_file = "prod.env"
