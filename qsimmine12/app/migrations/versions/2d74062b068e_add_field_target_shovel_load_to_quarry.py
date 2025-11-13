"""Add field target_shovel_load to Quarry

Revision ID: 2d74062b068e
Revises: 02142889870f
Create Date: 2025-11-06 10:36:58.524784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d74062b068e'
down_revision = '02142889870f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('quarry', sa.Column('target_shovel_load', sa.Float(), nullable=False, server_default='0.9'))



def downgrade():
    op.drop_column('quarry', 'target_shovel_load')
