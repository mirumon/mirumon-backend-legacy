from pydantic import PostgresDsn, RedisDsn, SecretStr

from app.settings.environments.base import AppSettings


class DevAppSettings(AppSettings):
    """Application settings with override params for dev environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = True

    title: str = "Dev Mirumon Service"

    # Auth settings
    secret_key: SecretStr = SecretStr("dev-secret-key")
    shared_key: SecretStr = SecretStr("dev-shared-key")

    # Infrastructure settings
    database_dsn: PostgresDsn = "postgres://postgres:postgres@localhost/postgres"
    redis_dsn: RedisDsn = "redis://user:pass@localhost:6379/redis"

    # First superuser credentials
    first_superuser_username: str = "dev-superuser"
    first_superuser_password: str = "dev-superuser-password"

    class Config(AppSettings.Config):
        env_file = ".env"
