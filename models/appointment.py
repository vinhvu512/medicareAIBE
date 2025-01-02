from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from database.session import Base
import enum

class AppointmentStatusEnum(str, enum.Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"
    IN_PROGRESS = "InProgress"

class Appointment(Base):
    __tablename__ = "appointments"

    m_appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    m_appointment_day = Column(DateTime, nullable=False)
    m_appointment_status = Column(Enum(AppointmentStatusEnum), nullable=False)
    m_appointment_reason = Column(String(255))
    m_patient_id = Column(Integer, ForeignKey('patients.m_patient_id'))
    m_doctor_id = Column(Integer, ForeignKey('doctors.m_doctor_id'))
    m_room_id = Column(Integer, ForeignKey('clinic_rooms.m_room_id'))
    m_hospital_id = Column(Integer, ForeignKey('hospitals.m_hospital_id'))