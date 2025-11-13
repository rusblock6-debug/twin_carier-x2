"""add_solver_type_to_scenario_table

Revision ID: 02142889870f
Revises: fa791c45aefa
Create Date: 2025-10-30 12:12:04.335413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02142889870f'
down_revision = 'fa791c45aefa'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('scenario', sa.Column('solver_type', sa.Integer(), nullable=False, server_default="1"))


def downgrade():
    op.drop_column('scenario', 'solver_type')
