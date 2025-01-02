from sqlalchemy import Column, Integer, String, ForeignKey
from database.session import Base

class Patient(Base):
    __tablename__ = "patients"

    m_patient_id = Column(Integer, ForeignKey('users.m_user_id'), primary_key=True)
    m_profile_image = Column(String(255))