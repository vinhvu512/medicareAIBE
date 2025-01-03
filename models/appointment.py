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

    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_day = Column(DateTime, nullable=False)
    appointment_status = Column(Enum(AppointmentStatusEnum), nullable=False)
    appointment_reason = Column(String(255))
    patient_id = Column(Integer, ForeignKey('patients.patient_id'))
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'))
    room_id = Column(Integer, ForeignKey('clinic_rooms.room_id'))
    hospital_id = Column(Integer, ForeignKey('hospitals.hospital_id'))