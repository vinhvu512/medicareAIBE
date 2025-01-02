from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from database.session import Base

class Doctor(Base):
    __tablename__ = "doctors"

    m_doctor_id = Column(Integer, ForeignKey('users.m_user_id'), primary_key=True)
    m_doctor_specialty = Column(String(255), nullable=False)
    m_doctor_experience = Column(Integer)
    m_profile_image = Column(String(255))