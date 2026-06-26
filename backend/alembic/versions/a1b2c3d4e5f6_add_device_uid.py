"""add stable uid to devices

Revision ID: a1b2c3d4e5f6
Revises: 5dda20127329
Create Date: 2026-06-26

Adds a nullable, unique ``uid`` column to the devices table so a device can be
matched across IP changes (DHCP renewal) instead of being duplicated. Existing
rows keep a NULL uid and get back-filled on the next discovery scan.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "5dda20127329"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("devices") as batch_op:
        batch_op.add_column(sa.Column("uid", sa.String(), nullable=True))
        batch_op.create_index("ix_devices_uid", ["uid"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("devices") as batch_op:
        batch_op.drop_index("ix_devices_uid")
        batch_op.drop_column("uid")
