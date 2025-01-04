from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, CheckConstraint
from database.session import Base
import enum
from datetime import date

class AppointmentStatusEnum(str, enum.Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled" 
    COMPLETED = "Completed"
    IN_PROGRESS = "InProgress"

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey('hospitals.hospital_id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.department_id'), nullable=False)
    room_id = Column(Integer, ForeignKey('clinic_rooms.room_id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    appointment_day = Column(Date, nullable=False)
    appointment_shift = Column(Integer, nullable=False)
    reason = Column(String(255))
    status = Column(Enum(AppointmentStatusEnum), nullable=False, default=AppointmentStatusEnum.SCHEDULED)

    __table_args__ = (
        CheckConstraint('appointment_shift >= 0 AND appointment_shift <= 19', 
                       name='check_valid_shift'),
    )