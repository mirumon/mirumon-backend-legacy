"""add groups and devices

Revision ID: 3dda3bee8e20
Revises: 61c8ff25f2ab
Create Date: 2019-12-08 02:16:16.102564

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, MACADDR, UUID

revision = "3dda3bee8e20"
down_revision = "61c8ff25f2ab"
branch_labels = None
depends_on = None


def create_device_groups() -> None:
    op.create_table(
        "device_groups",
        sa.Column(
            "id", UUID, server_default=text("uuid_generate_v4()"), primary_key=True
        ),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column(
            "user_id",
            UUID,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )

    op.execute(
        """
    INSERT INTO device_groups (name, user_id) 
    SELECT '__global__', id
    FROM users;
    """
    )


def create_devices() -> None:
    op.create_table(
        "devices",
        sa.Column(
            "id", UUID, server_default=text("uuid_generate_v4()"), primary_key=True
        ),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("mac_addr", MACADDR, nullable=False, index=True),
        sa.Column("data", JSONB),
    )
    op.create_table(
        "devices_to_groups",
        sa.Column("device_id", UUID, nullable=False),
        sa.Column("group_id", UUID, nullable=False),
    )


def upgrade() -> None:
    create_device_groups()
    create_devices()


def downgrade() -> None:
    op.drop_table("devices_to_groups")
    op.drop_table("devices")
    op.drop_table("device_groups")
