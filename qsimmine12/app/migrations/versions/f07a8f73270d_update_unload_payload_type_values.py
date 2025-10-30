"""Update Unload.payload_type values

Revision ID: f07a8f73270d
Revises: 5e034f7cece7
Create Date: 2025-07-30 14:13:40.016887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f07a8f73270d'
down_revision = '5e034f7cece7'
branch_labels = None
depends_on = None


def upgrade():
    unload = sa.sql.table(
        'unload',
        sa.sql.column('id', sa.Integer),
        sa.sql.column('payload_type', sa.Enum('GRAVEL', 'SAND', 'CLAY', 'WET_ORE', name='payloadtype'))
    )
    stmt = unload.update().values(payload_type='GRAVEL')
    op.execute(stmt)


def downgrade():
    pass
