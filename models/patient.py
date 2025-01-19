from sqlalchemy import Column, Integer, String, ForeignKey
from database.session import Base
from sqlalchemy.orm import relationship

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    profile_image = Column(String(255))

    health_reports = relationship("HealthReport", back_populates="patient")
