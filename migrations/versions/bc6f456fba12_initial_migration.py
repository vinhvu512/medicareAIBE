"""Initial migration

Revision ID: bc6f456fba12
Revises: 
Create Date: 2025-01-02 23:32:45.654060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc6f456fba12'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hospitals',
    sa.Column('m_hospital_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_hospital_name', sa.String(length=255), nullable=False),
    sa.Column('m_hospital_address', sa.String(length=255), nullable=True),
    sa.Column('m_hospital_phone', sa.String(length=15), nullable=True),
    sa.Column('m_hospital_email', sa.String(length=255), nullable=True),
    sa.Column('m_hospital_image', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('m_hospital_id')
    )
    op.create_table('users',
    sa.Column('m_user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_username', sa.String(length=255), nullable=False),
    sa.Column('m_email', sa.String(length=255), nullable=False),
    sa.Column('m_password', sa.String(length=255), server_default='1234', nullable=False),
    sa.Column('m_user_type', sa.Enum('DOCTOR', 'PATIENT', name='usertypeenum'), nullable=False),
    sa.Column('m_fullname', sa.String(length=255), nullable=False),
    sa.Column('m_date_of_birth', sa.Date(), nullable=False),
    sa.Column('m_gender', sa.Enum('MALE', 'FEMALE', 'OTHER', name='genderenum'), nullable=True),
    sa.Column('m_address', sa.String(length=255), nullable=True),
    sa.Column('m_phone', sa.String(length=15), nullable=True),
    sa.Column('m_profile_image', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('m_user_id'),
    sa.UniqueConstraint('m_email'),
    sa.UniqueConstraint('m_username')
    )
    op.create_table('departments',
    sa.Column('m_department_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_department_name', sa.String(length=255), nullable=False),
    sa.Column('m_department_location', sa.String(length=255), nullable=True),
    sa.Column('m_hospital_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['m_hospital_id'], ['hospitals.m_hospital_id'], ),
    sa.PrimaryKeyConstraint('m_department_id')
    )
    op.create_table('doctors',
    sa.Column('m_doctor_id', sa.Integer(), nullable=False),
    sa.Column('m_doctor_specialty', sa.String(length=255), nullable=False),
    sa.Column('m_doctor_experience', sa.Integer(), nullable=True),
    sa.Column('m_profile_image', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['m_doctor_id'], ['users.m_user_id'], ),
    sa.PrimaryKeyConstraint('m_doctor_id')
    )
    op.create_table('patients',
    sa.Column('m_patient_id', sa.Integer(), nullable=False),
    sa.Column('m_profile_image', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['m_patient_id'], ['users.m_user_id'], ),
    sa.PrimaryKeyConstraint('m_patient_id')
    )
    op.create_table('clinic_rooms',
    sa.Column('m_room_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_room_name', sa.String(length=255), nullable=False),
    sa.Column('m_room_location', sa.String(length=255), nullable=True),
    sa.Column('m_room_image', sa.String(length=255), nullable=True),
    sa.Column('m_department_id', sa.Integer(), nullable=True),
    sa.Column('m_hospital_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['m_department_id'], ['departments.m_department_id'], ),
    sa.ForeignKeyConstraint(['m_hospital_id'], ['hospitals.m_hospital_id'], ),
    sa.PrimaryKeyConstraint('m_room_id')
    )
    op.create_table('doctor_hospitals',
    sa.Column('m_relationship_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_doctor_id', sa.Integer(), nullable=True),
    sa.Column('m_hospital_id', sa.Integer(), nullable=True),
    sa.Column('m_work_schedule', sa.String(length=255), nullable=True),
    sa.Column('m_start_date', sa.Date(), nullable=False),
    sa.Column('m_end_date', sa.Date(), nullable=True),
    sa.Column('m_relationship_status', sa.Enum('ACTIVE', 'INACTIVE', 'PENDING', 'TERMINATED', name='relationshipstatusenum'), nullable=True),
    sa.ForeignKeyConstraint(['m_doctor_id'], ['doctors.m_doctor_id'], ),
    sa.ForeignKeyConstraint(['m_hospital_id'], ['hospitals.m_hospital_id'], ),
    sa.PrimaryKeyConstraint('m_relationship_id')
    )
    op.create_table('patient_doctor_relationships',
    sa.Column('m_relationship_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_patient_id', sa.Integer(), nullable=True),
    sa.Column('m_doctor_id', sa.Integer(), nullable=True),
    sa.Column('m_relationship_type', sa.String(length=50), nullable=False),
    sa.Column('m_relationship_status', sa.Enum('ACTIVE', 'INACTIVE', 'PENDING', 'TERMINATED', name='relationshipstatusenum'), nullable=False),
    sa.Column('m_relationship_start_date', sa.Date(), nullable=False),
    sa.Column('m_relationship_end_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['m_doctor_id'], ['doctors.m_doctor_id'], ),
    sa.ForeignKeyConstraint(['m_patient_id'], ['patients.m_patient_id'], ),
    sa.PrimaryKeyConstraint('m_relationship_id')
    )
    op.create_table('patient_hospitals',
    sa.Column('m_relationship_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_patient_id', sa.Integer(), nullable=True),
    sa.Column('m_hospital_id', sa.Integer(), nullable=True),
    sa.Column('m_relationship_type', sa.String(length=50), nullable=True),
    sa.Column('m_start_date', sa.Date(), nullable=False),
    sa.Column('m_end_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['m_hospital_id'], ['hospitals.m_hospital_id'], ),
    sa.ForeignKeyConstraint(['m_patient_id'], ['patients.m_patient_id'], ),
    sa.PrimaryKeyConstraint('m_relationship_id')
    )
    op.create_table('appointments',
    sa.Column('m_appointment_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('m_appointment_day', sa.DateTime(), nullable=False),
    sa.Column('m_appointment_status', sa.Enum('SCHEDULED', 'CANCELLED', 'COMPLETED', 'IN_PROGRESS', name='appointmentstatusenum'), nullable=False),
    sa.Column('m_appointment_reason', sa.String(length=255), nullable=True),
    sa.Column('m_patient_id', sa.Integer(), nullable=True),
    sa.Column('m_doctor_id', sa.Integer(), nullable=True),
    sa.Column('m_room_id', sa.Integer(), nullable=True),
    sa.Column('m_hospital_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['m_doctor_id'], ['doctors.m_doctor_id'], ),
    sa.ForeignKeyConstraint(['m_hospital_id'], ['hospitals.m_hospital_id'], ),
    sa.ForeignKeyConstraint(['m_patient_id'], ['patients.m_patient_id'], ),
    sa.ForeignKeyConstraint(['m_room_id'], ['clinic_rooms.m_room_id'], ),
    sa.PrimaryKeyConstraint('m_appointment_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('appointments')
    op.drop_table('patient_hospitals')
    op.drop_table('patient_doctor_relationships')
    op.drop_table('doctor_hospitals')
    op.drop_table('clinic_rooms')
    op.drop_table('patients')
    op.drop_table('doctors')
    op.drop_table('departments')
    op.drop_table('users')
    op.drop_table('hospitals')
    # ### end Alembic commands ###
