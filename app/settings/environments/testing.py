from pydantic import PostgresDsn, RedisDsn, SecretStr

from app.settings.environments.base import AppSettings


class TestAppSettings(AppSettings):
    """Application settings with override params for test environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = True

    title: str = "Test Mirumon Service"

    # Auth settings
    secret_key: SecretStr = SecretStr("test-secret-key")
    shared_key: SecretStr = SecretStr("test-shared-key")

    # Infrastructure settings
    database_dsn: PostgresDsn = "postgres://postgres:postgres@localhost/postgres"
    redis_dsn: RedisDsn = "redis://redis:redis@localhost/0"

    # First superuser credentials
    first_superuser_username: str = "test-superuser-username"
    first_superuser_password: str = "test-superuser-password"

    class Config(AppSettings.Config):
        env_file = "test.env"
