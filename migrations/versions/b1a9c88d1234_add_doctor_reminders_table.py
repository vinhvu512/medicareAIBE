from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union
# revision identifiers, used by Alembic.
revision = 'b1a9c88d1234'  # ID ngẫu nhiên cho file migration này
down_revision = 'fa4ed368167d'  # ID của migration cuối cùng trong hệ thống
branch_labels = None
depends_on = None


def upgrade():
    # Tạo bảng doctor_reminders
    op.create_table(
        'doctor_reminders',
        sa.Column('reminder_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('reminder_content', sa.String(length=255), nullable=False),
        sa.Column('reminder_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.appointment_id']),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.doctor_id']),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.patient_id']),
        sa.PrimaryKeyConstraint('reminder_id')
    )


def downgrade():
    # Xóa bảng doctor_reminders
    op.drop_table('doctor_reminders')