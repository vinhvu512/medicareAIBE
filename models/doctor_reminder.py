from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.session import Base
from datetime import datetime


class DoctorReminder(Base):
    __tablename__ = "doctor_reminders"

    reminder_id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey('appointments.appointment_id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    reminder_content = Column(String(255), nullable=False)
    reminder_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    appointment = relationship("Appointment", backref="doctor_reminders")
    doctor = relationship("Doctor", backref="doctor_reminders")
    patient = relationship("Patient", backref="doctor_reminders")