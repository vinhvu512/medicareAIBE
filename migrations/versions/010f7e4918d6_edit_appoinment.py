"""edit appoinment

Revision ID: 010f7e4918d6
Revises: 4d8c8bfde4ed
Create Date: 2025-01-04 01:17:12.350562
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '010f7e4918d6'
down_revision: Union[str, None] = '4d8c8bfde4ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop existing table and enum type if they exist
    op.execute('DROP TABLE IF EXISTS appointments CASCADE')
    op.execute('DROP TYPE IF EXISTS appointmentstatusenum CASCADE')

    # Create enum type using IF NOT EXISTS
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'appointmentstatusenum') THEN
                CREATE TYPE appointmentstatusenum AS ENUM 
                ('SCHEDULED', 'CANCELLED', 'COMPLETED', 'IN_PROGRESS');
            END IF;
        END
        $$;
    """)

    # Create new table
    op.create_table('appointments',
        sa.Column('appointment_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('appointment_day', sa.DateTime(), nullable=False),
        sa.Column('appointment_shift', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('status', postgresql.ENUM('SCHEDULED', 'CANCELLED', 'COMPLETED', 'IN_PROGRESS',
                                          name='appointmentstatusenum',
                                          create_type=False), 
                 nullable=False,
                 server_default='SCHEDULED'),
        sa.PrimaryKeyConstraint('appointment_id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.hospital_id']),
        sa.ForeignKeyConstraint(['department_id'], ['departments.department_id']),
        sa.ForeignKeyConstraint(['room_id'], ['clinic_rooms.room_id']),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.doctor_id']),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.patient_id']),
        sa.CheckConstraint('appointment_shift >= 0 AND appointment_shift <= 19',
                          name='check_valid_shift')
    )

def downgrade() -> None:
    # Drop table and enum type
    op.execute('DROP TABLE IF EXISTS appointments CASCADE')
    op.execute('DROP TYPE IF EXISTS appointmentstatusenum CASCADE')