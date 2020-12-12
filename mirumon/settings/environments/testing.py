from pydantic import AnyUrl, PostgresDsn, SecretStr

from mirumon.settings.environments.app import AppSettings


class TestAppSettings(AppSettings):
    """Application settings with override params for test environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = False

    title: str = "Test Mirumon Service"

    # Timeout settings
    rest_max_response_time: float = 2.0
    event_timeout: int = 2

    # Auth settings
    secret_key: SecretStr = SecretStr("test-secret-key")
    shared_key: SecretStr = SecretStr("test-shared-key")

    # Infrastructure settings
    postgres_dsn: PostgresDsn = "postgres://postgres:postgres@localhost/postgres"  # type: ignore  # noqa: E501
    rabbit_dsn: AnyUrl = "amqp://rabbitmq:rabbitmq@localhost"  # type: ignore

    class Config(AppSettings.Config):
        env_file = "test.env"
