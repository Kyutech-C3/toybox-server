"""add asset url

Revision ID: 70346d7f866a
Revises: cf50f054281b
Create Date: 2022-10-01 14:38:31.287606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70346d7f866a'
down_revision = 'cf50f054281b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asset', sa.Column('url', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('asset', 'url')
    # ### end Alembic commands ###