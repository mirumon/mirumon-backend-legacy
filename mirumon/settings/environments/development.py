from pydantic import AnyUrl, PostgresDsn, RedisDsn, SecretStr

from mirumon.settings.environments.app import AppSettings


class DevAppSettings(AppSettings):
    """Application settings with override params for dev environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = True

    title: str = "Dev Mirumon Service"

    # Auth settings
    secret_key: SecretStr = SecretStr("dev-secret-key")
    shared_key: SecretStr = SecretStr("dev-shared-key")

    # Infrastructure settings
    postgres_dsn: PostgresDsn = (
        "postgres://postgres:postgres@localhost/postgres"  # type:ignore
    )
    rabbit_dsn: AnyUrl = "amqp://rabbitmq:rabbitmq@localhost"  # type:ignore
    redis_dsn: RedisDsn = "redis://user:redis@localhost/0"

    class Config(AppSettings.Config):
        env_file = ".env"
