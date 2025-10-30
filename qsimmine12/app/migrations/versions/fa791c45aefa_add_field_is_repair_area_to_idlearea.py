"""Add field is_repair_area to IdleArea

Revision ID: fa791c45aefa
Revises: 9daa452a370b
Create Date: 2025-10-24 06:14:12.764161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa791c45aefa'
down_revision = '9daa452a370b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('idle_area', sa.Column('is_repair_area', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('idle_area', 'is_blast_waiting_area')
