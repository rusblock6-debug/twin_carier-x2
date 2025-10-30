"""Rename ShiftChangeArea to IdleArea

Revision ID: 8520318762c4
Revises: fea74ce0faa7
Create Date: 2025-09-15 16:17:12.435756

"""
from alembic import op
import sqlalchemy as sa

revision = '8520318762c4'
down_revision = 'fea74ce0faa7'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('shift_change_area', 'idle_area')
    op.add_column('idle_area', sa.Column('is_lunch_area', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('idle_area', sa.Column('is_shift_change_area', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('idle_area', sa.Column('is_blast_waiting_area', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('idle_area', 'is_blast_waiting_area')
    op.drop_column('idle_area', 'is_shift_change_area')
    op.drop_column('idle_area', 'is_lunch_area')
    op.rename_table('idle_area', 'shift_change_area')
