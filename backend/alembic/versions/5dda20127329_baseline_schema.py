"""baseline_schema

Revision ID: 5dda20127329
Revises: 
Create Date: 2025-11-23 12:30:40.524942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '5dda20127329'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. Create Independent Tables ---
    op.create_table('devices',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=False),
        sa.Column('ip', sa.VARCHAR(), nullable=False),
        sa.Column('raw_data', sqlite.JSON(), nullable=True),
        sa.Column('type', sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('audio_files',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=False),
        sa.Column('blob', sa.BLOB(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    op.create_table('cities',
        sa.Column('id', sa.INTEGER(), nullable=True),
        sa.Column('name', sa.TEXT(), nullable=True),
        sa.Column('lat', sa.REAL(), nullable=True),
        sa.Column('lon', sa.REAL(), nullable=True),
        sa.Column('country', sa.TEXT(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for cities
    with op.batch_alter_table('cities', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('idx_name_country'), ['name', 'country'], unique=False)
        batch_op.create_index(batch_op.f('idx_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('idx_country'), ['country'], unique=False)

    # --- 2. Create Dependent Tables (Settings) ---
    # Settings depends on audio_files, cities, and devices, so it must be created last.
    op.create_table('settings',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('volume', sa.INTEGER(), nullable=False),
        sa.Column('enable_scheduler', sa.BOOLEAN(), nullable=False),
        sa.Column('selected_method', sa.VARCHAR(), nullable=True),
        sa.Column('force_date', sa.DATE(), nullable=True),
        sa.Column('city_id', sa.INTEGER(), nullable=True),
        sa.Column('device_id', sa.INTEGER(), nullable=False),
        sa.Column('audio_id', sa.INTEGER(), nullable=True),
        sa.ForeignKeyConstraint(['audio_id'], ['audio_files.id'], ),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # --- Drop tables in reverse order ---
    op.drop_table('settings')
    
    with op.batch_alter_table('cities', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('idx_country'))
        batch_op.drop_index(batch_op.f('idx_name'))
        batch_op.drop_index(batch_op.f('idx_name_country'))
    op.drop_table('cities')
    
    op.drop_table('audio_files')
    op.drop_table('devices')