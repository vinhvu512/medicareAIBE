"""add department to doctor hospital relationship

Revision ID: 7b145e450036
Revises: 867dff8f0a93
Create Date: 2025-01-03 22:45:32.379895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b145e450036'
down_revision: Union[str, None] = '867dff8f0a93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doctor_hospitals', sa.Column('department_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'doctor_hospitals', 'departments', ['department_id'], ['department_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'doctor_hospitals', type_='foreignkey')
    op.drop_column('doctor_hospitals', 'department_id')
    # ### end Alembic commands ###
