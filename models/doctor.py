from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from database.session import Base

class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    doctor_specialty = Column(String(255), nullable=False)
    doctor_experience = Column(Integer)
    profile_image = Column(String(255))