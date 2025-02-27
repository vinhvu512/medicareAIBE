"""add weekly_schedule to doctor

Revision ID: 4d8c8bfde4ed
Revises: 7b145e450036
Create Date: 2025-01-04 00:54:56.736471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d8c8bfde4ed'
down_revision: Union[str, None] = '7b145e450036'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("UPDATE doctors SET doctor_experience = 0 WHERE doctor_experience IS NULL")

    op.add_column('doctors', sa.Column('weekly_schedule', sa.JSON(), nullable=True))
    op.alter_column('doctors', 'doctor_experience',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('doctors', 'doctor_experience',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('doctors', 'weekly_schedule')
    # ### end Alembic commands ###
