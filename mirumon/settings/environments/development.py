from pydantic import AnyUrl, PostgresDsn, SecretStr

from mirumon.settings.environments.base import AppSettings


class DevAppSettings(AppSettings):
    """Application settings with override params for dev environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = True

    title: str = "Dev Mirumon Service"

    # Auth settings
    secret_key: SecretStr = SecretStr("dev-secret-key")
    shared_key: SecretStr = SecretStr("dev-shared-key")

    # Infrastructure settings
    postgres_dsn: PostgresDsn = "postgres://postgres:postgres@localhost/postgres"
    rabbit_dsn: AnyUrl = "amqp://rabbitmq:rabbitmq@localhost"

    class Config(AppSettings.Config):
        env_file = ".env"
