"""add users table

Revision ID: 61c8ff25f2ab
Revises:
Create Date: 2019-12-01 15:12:34.692592

"""
from typing import Tuple, Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import UUID

from app.settings.components import jwt
from app.settings.config import get_app_settings

revision = "61c8ff25f2ab"
down_revision = None
branch_labels = None
depends_on = None


def register_uuid_extension() -> None:
    op.execute(
        """
    CREATE EXTENSION "uuid-ossp"
    """,
    )


def create_updated_at_trigger() -> None:
    op.execute(
        """
    CREATE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS
    $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """,
    )


def timestamps() -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )


def create_users_table() -> Any:
    users = op.create_table(
        "users",
        sa.Column(
            "id", UUID, server_default=text("uuid_generate_v4()"), primary_key=True,
        ),
        sa.Column("username", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("scopes", sa.ARRAY(sa.String)),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """,
    )
    return users


def create_first_super_user(users_table) -> None:
    settings = get_app_settings()
    salt = jwt.generate_salt()
    hashed_password = jwt.get_password_hash(salt + settings.first_superuser_password)
    op.bulk_insert(
        users_table,
        [
            {
                "username": settings.first_superuser_username,
                "hashed_password": hashed_password,
                "salt": salt,
                "scopes": settings.initial_superuser_scopes,
            },
        ],
    )


def upgrade() -> None:
    register_uuid_extension()
    create_updated_at_trigger()
    users = create_users_table()
    create_first_super_user(users)


def downgrade() -> None:
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")
    op.execute(
        """
    DROP EXTENSION "uuid-ossp"
    """,
    )
