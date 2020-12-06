import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from mirumon.settings.config import get_app_settings

project_root_dir = pathlib.Path(__file__).resolve().parents[3]
sys.path.append(str(project_root_dir))

config = context.config

fileConfig(config.config_file_name)

target_metadata = None  # type: ignore

dsn = str(get_app_settings().postgres_dsn)
config.set_main_option("sqlalchemy.url", dsn)


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
