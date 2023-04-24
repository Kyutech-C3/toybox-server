"""alter_discord_user_id_length

Revision ID: 3a98fa6461c5
Revises: f03c01296e25
Create Date: 2023-04-23 16:28:42.873555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3a98fa6461c5"
down_revision = "f03c01296e25"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "user",
        "discord_user_id",
        existing_type=sa.String(18),
        type=sa.String(255),
    )


def downgrade():
    op.alter_column(
        "user", "discord_user_id", existing_type=sa.String(255), type_=sa.String(18)
    )
