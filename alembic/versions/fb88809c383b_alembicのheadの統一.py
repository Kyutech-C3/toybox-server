"""alembicのheadの統一

Revision ID: fb88809c383b
Revises: 70346d7f866a, 543bc3330fe5
Create Date: 2022-10-13 13:18:45.011523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb88809c383b'
down_revision = ('70346d7f866a', '543bc3330fe5')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
