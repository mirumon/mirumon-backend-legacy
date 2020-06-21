from pydantic import PostgresDsn, RedisDsn, SecretStr

from app.settings.environments.base import AppSettings


class TestAppSettings(AppSettings):
    """Application settings with override params for test environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = True

    title: str = "Mirumon Test Service"

    # Auth settings
    secret_key: SecretStr = SecretStr("secret-test-key")
    shared_key: SecretStr = SecretStr("shared-test-key")

    # Infrastructure settings
    database_dsn: PostgresDsn = "postgres://postgres:postgres@localhost/postgres"
    redis_dsn: RedisDsn = "redis://user:pass@localhost:6379/redis"

    # First superuser credentials
    first_superuser: str = "test-superuser"
    first_superuser_password: str = "test_superuser_password"

    class Config(AppSettings.Config):
        env_file = "test.env"
