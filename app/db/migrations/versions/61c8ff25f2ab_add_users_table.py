"""add users table

Revision ID: 61c8ff25f2ab
Revises: 
Create Date: 2019-12-01 15:12:34.692592

"""
from typing import Tuple

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import UUID

from app.common.config import (
    FIRST_SUPERUSER,
    FIRST_SUPERUSER_PASSWORD,
    INITIAL_SUPERUSER_SCOPES,
)
from app.models.domain.users import UserInDB

revision = "61c8ff25f2ab"
down_revision = None
branch_labels = None
depends_on = None


def register_uuid_extension() -> None:
    op.execute(
        """
    CREATE EXTENSION "uuid-ossp"
    """
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
    """
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


def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id", UUID, server_default=text("uuid_generate_v4()"), primary_key=True
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
        """
    )


def upgrade() -> None:
    register_uuid_extension()
    create_updated_at_trigger()
    create_users_table()

    admin_user = UserInDB(username=FIRST_SUPERUSER, scopes=INITIAL_SUPERUSER_SCOPES)
    admin_user.change_password(str(FIRST_SUPERUSER_PASSWORD))

    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO users(username, salt, hashed_password, scopes) 
            VALUES (:username, :salt, :hashed_password, :scopes)
        """,
        ),
        dict(
            username=admin_user.username,
            salt=admin_user.salt,
            hashed_password=admin_user.hashed_password,
            scopes=[scope.value for scope in admin_user.scopes],
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")
