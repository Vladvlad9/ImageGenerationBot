"""02_model_user_settings

Revision ID: 9a3f2c7d1b80
Revises: 53483398a890
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a3f2c7d1b80'
down_revision: Union[str, Sequence[str], None] = '53483398a890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_settings',
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('image_aspect_ratio', sa.String(length=16), nullable=False),
        sa.Column('image_quality', sa.String(length=16), nullable=False),
        sa.Column('language', sa.String(length=8), nullable=False),
        sa.Column('notify_on_finish', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, comment='Date of created'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, comment='Date of last updated'),
        sa.ForeignKeyConstraint(['telegram_id'], ['user.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('telegram_id'),
    )
    op.create_index(
        op.f('ix_user_settings_telegram_id'),
        'user_settings',
        ['telegram_id'],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_settings_telegram_id'), table_name='user_settings')
    op.drop_table('user_settings')
